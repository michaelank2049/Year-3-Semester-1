#!"C:\Python\python.exe"

##from dbconfig import *
import pymysql
import cgi
import cgitb
cgitb.enable()

#	Establish a cursor for MySQL connection.
##db = get_mysql_param()
cnx = pymysql.connect(user='lankfordm0772', 
                      password='Aggie1510800',
                      host='localhost',
                      # port needed only if it is not the default number, 3306.
                      # port = int(db['port']), 
                      database='SWIM')
                      
cursor = cnx.cursor()

#	Create HTTP response header
print("Content-Type: text/html;charset=utf-8")
print()

#	Create a primitive HTML starter
print ('''<html>
<head></head>
<body>
''')

#	Get HTTP parameter, ctid (caretaker id) and sid (swimmer id)
form = cgi.FieldStorage()
sid = form.getfirst('sid')

if sid is None:
    #	No HTTP parameter: show all levels and swimmer in the levels
    print('<h3>Levels with swimmers</h3>')
    print('<ol>')

    #	SQL solution including the bonus feature for getting
    #	the number of swimmers in a level.
    query = '''
WITH t1 AS (
SELECT DISTINCT l.levelId, l.level,
	COUNT(lh.swimmerId) AS n_swimmers
FROM level AS l INNER JOIN levelHistory AS lh ON (l.levelId = lh.levelId)
GROUP BY l.levelId, l.level),
t2 AS (
SELECT DISTINCT lh.levelId, 
	GROUP_CONCAT(CONCAT('    <li><a href="?sid=', s.swimmerId, '">', s.fName, ' ', s.lName, '</a>: ',
		IF(lh.levelId = s.currentLevelId, 'current', 'past'), ' level since ', lh.startDate, '</li>\n') SEPARATOR '')
		AS swimmers
FROM levelHistory AS lh INNER JOIN swimmer AS s ON (lh.swimmerId = s.swimmerId)
GROUP BY  lh.levelId
)
SELECT DISTINCT t1.levelId, t1.level, t1.n_swimmers, t2.swimmers
FROM t1 INNER JOIN t2 ON (t1.levelId = t2.levelId);
'''
    cursor.execute(query)
    print('<ol>')
    for (level_id, level, n_swimmers, swimmers) in cursor:
        print('<li>Level #:' + str(level_id)
        + ' (' + level + '): ' + str(n_swimmers) 
			+ ' achieved: \n<ol>\n' + swimmers + '</ol></li>\n')
	
    print('</ol>')
    print('</body></html>')
    cursor.close()
    cnx.close()		
    quit()
	
if sid is not None:	#	This will always be satisfied at this point.
	#	Show swimmer information.
	query = '''
SELECT CONCAT(s.fName, ' ', s.LName) AS swimmer, 
	COUNT(p.EventId) AS n_events,
	GROUP_CONCAT(CONCAT('   <li>', m.title, ': ',
            e.title, '.</li>\n') SEPARATOR '') AS events
FROM swimmer AS s INNER JOIN participation AS p ON (s.swimmerId = p.swimmerId)
	INNER JOIN event AS e ON (p.eventId = e.eventId)
	INNER JOIN meet AS m ON (e.meetId = m.meetId)
WHERE s.swimmerId =%s
'''

	cursor.execute(query,(int(sid),))
	(swimmer, count, events) = cursor.fetchone()
	
	print('<p>Swimmer #' + str(sid) + ' ' +
			swimmer + ': participated in ' + str(count) + ' events.\n' +
            '<ol>' + events + '</ol>')
                  
cursor.close()
cnx.close()		
				  
print ('''</body>
</html>''')

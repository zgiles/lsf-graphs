<?php

$dbhost = 'db1.example.local';
$dbusername = 'lsfstats';
$dbpassword = 'lsfstats';
$dbname = 'lsfstats';

mysql_connect($dbhost, $dbusername, $dbpassword) or die(mysql_error());
mysql_select_db($dbname) or die(mysql_error());


$importnames = shell_exec('cat names');
foreach (split("\n", $importnames) as $name) {
	if (strpos($name,':') !== false) {
		$parts = split(":", $name);
		echo "$name --- $parts[0] --- $parts[1]\n";
		$query = "insert into lsfstats.namedictionary (id, shortname, longname) VALUES ( DEFAULT, '$parts[0]', '$parts[1]');";
		$sth = mysql_query($query);
		$rows = array();
		while($r = mysql_fetch_assoc($sth)) {
 		   $rows[] = $r;
		}
print json_encode($rows);
	}
}



?>

<?php

include("cache_header.php");
include("cred.php");

mysql_connect($dbhost, $dbusername, $dbpassword) or die(mysql_error()); 
mysql_select_db($dbname) or die(mysql_error());

$end = ( isset($_GET['end']) && $_GET['end'] != '' && is_int(intval($_GET['end'])) ? mysql_real_escape_string(intval($_GET['end'])) : intval(time() - 60) );
$start = ( isset($_GET['start']) && $_GET['end'] != '' && is_int(intval($_GET['start'])) ? mysql_real_escape_string(intval($_GET['start'])) : intval($end - (180*60)) );
$field = ( isset($_GET['field']) && $_GET['field'] != '' ? mysql_real_escape_string($_GET['field']) : false );
$user = ( isset($_GET['user']) && $_GET['user'] != '' ? mysql_real_escape_string($_GET['user']) : false );
$type = ( isset($_GET['type']) && $_GET['type'] != '' ? mysql_real_escape_string($_GET['type']) : "summary" );
$sort = ( isset($_GET['sort']) && $_GET['sort'] != '' ? mysql_real_escape_string($_GET['sort']) : false );
$dictionary = ( isset($_GET['dictionary']) && $_GET['dictionary'] != '' ? true : false );

if($type == "instant") {
	$field = ( $field ? $field : "cores" );
	$user = ( $user ? " and jobs.user = '$user' " : "" );
	$sort = ( $sort ? $sort : $field );
	$query = "select jobs.timestamp, jobs.user as user, count(jobs.user) as user_count, sum(jobs.mem) as mem, sum(job.mem_reservation) as mem_reservation, sum(jobs.mem_max) as mem_max, sum(jobs.mem_avg)/count(jobs.mem_avg) as mem_avg, sum(jobs.cores) as cores, count(jobs.cores) as running_jobs from jobs, (select timestamp from jobs group by 1 order by 1 desc limit 1,1) as b where jobs.timestamp = b.timestamp and jobs.status = 4 $user group by 2 order by $sort desc;";
}
if($type == "xpery") {
	$field = ( $field ? $field : "user" ); # how many anything per user, how many cores per memory region, etc
	$user = ( $user ? " and jobs.user = '$user' " : "" );
	$sort = ( $sort ? $sort : 'token' );
	if($dictionary) {
		$longname = "IFNULL( namedictionary.longname, jobs.$field) as longname,";
		$longnamejoin = " LEFT JOIN namedictionary as namedictionary on jobs.$field = namedictionary.shortname"; 
		$longnamegroup = ", longname";
	} else {
		$longname = "";
		$longnamejoin = "";
		$longnamegroup = "";
	}
	$query = "select jobs.timestamp, jobs.$field as token, $longname count(jobs.user) as user_count, sum(jobs.mem) as mem, sum(jobs.mem_reservation) as mem_reservation, sum(jobs.mem_max) as mem_max, sum(jobs.mem_avg)/count(jobs.mem_avg) as mem_avg, sum(jobs.cores) as cores, count(jobs.cores) as running_jobs from jobs $longnamejoin, (select timestamp from jobs group by 1 order by 1 desc limit 2,1) as b where jobs.timestamp = b.timestamp and jobs.status = 4 $user group by token $longnamegroup, timestamp order by $sort desc;";
}
if($type == "summary") {
	$queryfields = ( $field ? "timestamp, $field" : "*" );
	if ( $user ) {
		$query = " SELECT jobst.timestamp as timestamp, jobst.user as user, jobst.user_count as user_count, IFNULL( jobsr.mem, 0) as mem, IFNULL( jobsr.mem_reservation, 0) as mem_reservation, IFNULL( jobsr.mem_max, 0) as mem_max, IFNULL( jobsr.mem_avg, 0) as mem_avg, IFNULL( jobsr.cores, 0) as cores, IFNULL( jobsp.pending_jobs, 0) as pending_jobs, IFNULL( jobsr.running_jobs, 0) as running_jobs, IFNULL( jobsa.total_jobs, 0 ) as total_jobs, IFNULL( jobsp.pending_time_avg, 0) as pending_time_avg FROM ( SELECT timestamp as timestamp, user, count(user) as user_count FROM $dbname.jobs WHERE timestamp >= $start and timestamp <= $end and user = '$user' GROUP BY timestamp ) as jobst LEFT JOIN ( SELECT timestamp, count(*) as pending_jobs, abs(sum(submit_time)-($end*count(submit_time)))/count(submit_time) as pending_time_avg FROM $dbname.jobs FORCE INDEX(timestamp_user) WHERE status = 1 and timestamp >= $start and timestamp <= $end and user = '$user' GROUP BY timestamp ) as jobsp ON jobst.timestamp = jobsp.timestamp LEFT JOIN ( SELECT timestamp, sum(mem) as mem, sum(mem_reservation) as mem_reservation, sum(mem_max) as mem_max, sum(mem_avg)/count(mem_avg) as mem_avg, sum(cores) as cores, count(*) as running_jobs FROM $dbname.jobs FORCE INDEX(timestamp_user) WHERE status=4 and timestamp >= $start and timestamp <= $end and user = '$user' GROUP BY timestamp ) as jobsr ON jobst.timestamp = jobsr.timestamp LEFT JOIN ( SELECT timestamp, count(*) as total_jobs FROM $dbname.jobs FORCE INDEX(timestamp_user) WHERE timestamp >= $start and timestamp <= $end and user = '$user' GROUP BY timestamp ) as jobsa ON jobst.timestamp = jobsa.timestamp WHERE jobst.timestamp >= $start and jobst.timestamp <= $end GROUP BY timestamp ORDER BY timestamp asc; ";
	} else { 
		$query = "select $queryfields from summary where timestamp >= $start and timestamp <= $end order by timestamp asc;";
	}

}
$sth = mysql_query($query);
$rows = array();
while($r = mysql_fetch_assoc($sth)) {
    $rows[] = $r;
//    print $r['timestamp'] . "," . $r['br'] . PHP_EOL;
}
print json_encode($rows);

include("cache_footer.php");

?>

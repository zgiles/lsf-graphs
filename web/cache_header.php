<?php
// Just a test...
// http://www.xeweb.net/2010/01/15/simple-php-caching/
$cache_expires = 120;
$cache_folder = "/dev/shm/";

function is_cached($file) {
 global $cache_folder, $cache_expires;
 $cachefile = $cache_folder . $file;
 $cachefile_created = (file_exists($cachefile)) ? @filemtime($cachefile) : 0;
 return ((time() - $cache_expires) < $cachefile_created);
}

function read_cache($file) {
 global $cache_folder;
 $cachefile = $cache_folder . $file;
 return file_get_contents($cachefile);
}

function write_cache($file, $out) {
 global $cache_folder;
 $cachefile = $cache_folder . $file;
 $fp = fopen($cachefile, 'w');
 fwrite($fp, $out);
 fclose($fp);
}

$cache_file = md5($_SERVER['REQUEST_URI']) . '.cache';

if (is_cached($cache_file)) {
 echo read_cache($cache_file);
 exit();
}

ob_start();

?>

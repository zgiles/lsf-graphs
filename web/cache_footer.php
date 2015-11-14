<?php

$cache_contents = ob_get_contents();
write_cache($cache_file, $cache_contents);

?>

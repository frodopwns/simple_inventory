<?php

$conf['site_name'] = "{{ site }}";

$conf["install_profile"] = "{{ profile }}";
$conf["cu_sid"] = "{{ sid }}";
$conf['varnish_version'] = 3;
$path = "{{ sid }}";

{% if status in ['launched', 'launching'] %}
$launched = TRUE;
$conf["cu_path"] = "{{ path }}";
{% else %}
$launched = FALSE;
{% endif %}

if ($launched) {
   if (isset($_SERVER['WWWNG_ENV'])) {

   {% if status in ['launched', 'launching'] %}
   $path = '{{ path }}';
   {% else %}
   $path = 'PATH_PLACEHOLDER';
   {% endif %}

     if ($_SERVER['HTTP_HOST'] == 'poros' &&
       strpos($_SERVER['REQUEST_URI'], $conf['cu_sid']) !== false) {
       header('HTTP/1.0 301 Moved Permanently');
       header('Location: http://poros'. str_replace($conf['cu_sid'], $path, $_SERVER['REQUEST_URI']));
       exit();
     }
   }
}

$databases = array (
  'default' => 
  array (
    'default' => 
    array (
      'database' => '{{ sid }}',
      'username' => 'root',
      'password' => 'root',
      'host' => 'localhost',
      'port' => '',
      'driver' => 'mysql',
      'prefix' => '',
    ),
  ),
);

/**
 * Access control for update.php script.
 *
 * If you are updating your Drupal installation using the update.php script but
 * are not logged in using either an account with the "Administer software
 * updates" permission or the site maintenance account (the account that was
 * created during installation), you will need to modify the access check
 * statement below. Change the FALSE to a TRUE to disable the access check.
 * After finishing the upgrade, be sure to open this file again and change the
 * TRUE back to a FALSE!
 */
$update_free_access = FALSE;

/**
 * Salt for one-time login links and cancel links, form tokens, etc.
 *
 * This variable will be set to a random value by the installer. All one-time
 * login links will be invalidated if the value is changed. Note that if your
 * site is deployed on a cluster of web servers, you must ensure that this
 * variable has the same value on each server. If this variable is empty, a hash
 * of the serialized database credentials will be used as a fallback salt.
 *
 * For enhanced security, you may set this variable to a value using the
 * contents of a file outside your docroot that is never saved together
 * with any backups of your Drupal files and database.
 *
 * Example:
 *   $drupal_hash_salt = file_get_contents('/home/example/salt.txt');
 *
 */
$drupal_hash_salt = 'dg2jsRi4LW_AMer4gX3Nv0AAj3ZwEwUck4NCIFLafEU';

// $base_url = 'http://www.example.com';  // NO trailing slash!

/**
 * Some distributions of Linux (most notably Debian) ship their PHP
 * installations with garbage collection (gc) disabled. Since Drupal depends on
 * PHP's garbage collection for clearing sessions, ensure that garbage
 * collection occurs by using the most common settings.
 */
ini_set('session.gc_probability', 1);
ini_set('session.gc_divisor', 100);

/**
 * Set session lifetime (in seconds), i.e. the time from the user's last visit
 * to the active session may be deleted by the session garbage collector. When
 * a session is deleted, authenticated users are logged out, and the contents
 * of the user's $_SESSION variable is discarded.
 */
ini_set('session.gc_maxlifetime', 200000);

/**
 * Set session cookie lifetime (in seconds), i.e. the time from the session is
 * created to the cookie expires, i.e. when the browser is expected to discard
 * the cookie. The value 0 means "until the browser is closed".
 */
ini_set('session.cookie_lifetime', 2000000);


# $conf['site_name'] = 'My Drupal site';
# $conf['theme_default'] = 'garland';
# $conf['anonymous'] = 'Visitor';


$conf['404_fast_paths_exclude'] = '/\/(?:styles)\//';
$conf['404_fast_paths'] = '/\.(?:txt|png|gif|jpe?g|css|js|ico|swf|flv|cgi|bat|pl|dll|exe|asp)$/i';
$conf['404_fast_html'] = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.0//EN" "http://www.w3.org/MarkUp/DTD/xhtml-rdfa-1.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head><title>404 Not Found</title></head><body><h1>Not Found</h1><p>The requested URL "@path" was not found on this server.</p></body></html>';


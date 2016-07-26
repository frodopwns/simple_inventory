<?php
  
#drupal_get_path
#print_r($list['views']);

$results = array();
$module_list = system_rebuild_module_data();
foreach($module_list as $mn => $val) {
  $results[$mn]['machine_name'] = $mn;
  $results[$mn]['name'] = $val->info['name'];
  $results[$mn]['path'] = $val->uri;
  $status = "enabled";
  if ($val->status == 0) {
    $status = "disabled";
  }
  $results[$mn]['status'] = $status;
  $results[$mn]['type'] = $val->type;
  $results[$mn]['description'] = $val->info['description'];
}

echo drupal_json_encode($results);

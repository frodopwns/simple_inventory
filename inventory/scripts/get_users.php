<?php

/**
 * Takes a list of role ids and returns a list of role names instead
 */
function _roles_from_rids($rids) {
  $roles = array();
  foreach ($rids as $rid) {
    if ($rid != 2) {
      $roles[] = user_role_load($rid)->name;
    }
  }
  return $roles;
}

$query = db_select('users', 'u');
$query->fields('u', array('name', 'uid'));
$result = $query->execute();
$out = array();
while($record = $result->fetchAssoc()) {
  if (!empty($record) && $record['uid'] != 0 && $record['uid'] != 1) {
    $account = user_load((integer)$record['uid']);
    $roles = _roles_from_rids(array_keys($account->roles));
    if (!empty($roles)) {
      $out[] = array(
        "username" => $account->name,
        "mail" => $account->mail,
        "roles" => $roles,
      );
    }
  }
}
echo drupal_json_encode($out);

<?php

function check_site() {
  //check if nobody has logged in recently
  $query = db_select('users', 'u');
  $query->fields('u', array('name', 'uid'));
  $result = $query->execute();
  $access_list = array(0);
  while($record = $result->fetchAssoc()) {
    if (!empty($record) && $record['uid'] != 0 && $record['uid'] != 1) {
      $account = user_load((integer)$record['uid']);
      if ($account->access !== '0') {
        $access_list[] = (integer) $account->access;
      }
    }
  }
  //if noone has logged in ever then count days from creation date
  $most_recent = max($access_list);
  if ($most_recent == 0) {
    $most_recent = _get_site_created_date();
  }
  //86400 seconds in a day
  $days = (time() - $most_recent)/86400;
  //if it has been 30 or more days and the site is not launched
  //then think about sending notifications
  echo $days;
}

check_site();

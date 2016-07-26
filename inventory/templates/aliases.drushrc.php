<?php

// drush site alias file created 20140520-17:17:27 by mk-drush-aliases

$user = 'dplagnt';
{% for env in servers %}
// ============================================================================
// =========== {{ env }} host aliases ==========
{% for host in servers[env] %}
$aliases['{{ host }}'] = array(
  'remote-host' => '{{ host }}',
  'remote-user' => $user,
);
{% endfor -%}
{% endfor -%}
{% for env in servers %}
{% for site in sites %}
// ============================================================================
// ========= {{ env }} site aliases for site {{ site.name }}
{% for host in servers[env] %}
$aliases['{{ host }}-{{ site.sid }}'] = array(
  'uri' => '{{ host }}/{{ site.sid }}',
  'root' => '/data/releases/{{ site.sid }}/current',
  'parent' => '@{{ host }}',
);
{% endfor %}
$aliases['{{ env }}-{{ site.sid }}'] = array(
  'site-list' => array({% for host in servers[env] -%}'@{{ host }}-{{ site.sid }}',{% endfor %}),
);
{% endfor %}
{% endfor %}

{% for env in servers %}
// ============================================================================
// =============== {{ env }} site list aliases  ===============

$aliases['{{ env }}'] = array(
  'site-list' => array({% for site in sites -%}'@{{ env }}-{{ site.sid }}',{% endfor %}),
);
{% endfor %}

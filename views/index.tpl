% rebase('base.tpl', title='Overview')

<ul class="pure-menu-list">
  % for pcap in pcap_list:
    <li class="pure-menu-item"><a class="pure-menu-link" href="/show/{{pcap}}">{{pcap}}</a></li>
  % end
</ul>

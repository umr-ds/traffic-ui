% rebase('base.tpl', title='Overview')

<table class="pure-table pure-table-striped">
<thead>
  <tr>
    <th>Filename</th>
    <th>Ratings</th>
  </tr>
</thead>
<tbody>
  % for flow in flows:
  <tr>
    <td><a class="pure-menu-link" href="/show/{{flow[0]}}">{{flow[0]}}</a></td>
    <td>{{', '.join(flow[1])}}</td>
  </tr>
  % end
</tbody>
</table>

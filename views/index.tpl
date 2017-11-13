% rebase('base.tpl', title='Overview')

<form class="pure-form">
  <fieldset id="overview-tbl-fieldset">
    <input type="text" class="pure-input-2-3" id="overview-tbl-in">
    <button onclick="overviewTblForm()" class="pure-button pure-button-primary">Search</button>
  </fieldset>
</form>

<table class="pure-table pure-table-striped">
<thead>
  <tr>
    <th>Filename</th>
    <th>Ratings</th>
  </tr>
</thead>
<tbody id="overview-tbl-body">
</tbody>
</table>

<script>
  var query = window.location.hash;
  if (query.charAt(0) == '#') {
    query = query.substr(1);
  }

  overviewTbl(query);

  var input = document.getElementById('overview-tbl-in');
  input.value = query;
</script>

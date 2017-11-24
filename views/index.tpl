% rebase('base.tpl', title='Flows', ratings=ratings)

<form class="pure-form">
  <fieldset id="overview-tbl-fieldset">
    <input type="text" class="pure-input-2-3" id="overview-tbl-in">
    <button onclick="overviewTblForm()" class="pure-button pure-button-primary">Search</button>
  </fieldset>
</form>

<ul class="pure-menu-list" id="search-history">
</ul>

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
  updateQuery();

  window.onhashchange = updateQuery;
</script>

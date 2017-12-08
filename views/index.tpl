% rebase('base.tpl', title='Flows', ratings=ratings)

<form class="pure-form">
  <fieldset id="overview-tbl-fieldset">
    <input type="text" class="pure-input" id="overview-tbl-in">
    <button class="pure-button pure-button-primary" id="overview-tbl-btn">Search</button>
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
  updateQuery();

  window.onhashchange = function() {
    updateQuery();
    searchHistory(awesome);
  };

  var btn = document.getElementById('overview-tbl-btn');
  btn.addEventListener('click', function(event) {
    event.preventDefault();
    overviewTblForm();
  });

  var input = document.getElementById('overview-tbl-in');
  input.addEventListener('awesomplete-selectcomplete', function(event) {
    overviewTblForm();
  });

  var awesome = new Awesomplete(input, {
	  list: [],
    minChars: 1
  });
  searchHistory(awesome);

  input.parentElement.classList.add('pure-u-2-3');
</script>

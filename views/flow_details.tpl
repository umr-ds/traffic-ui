% rebase('base.tpl', title='Flowdetails', subtitle=filename)

<div class="pure-g">
  <div class="pure-u-5-6">
    <img class="pure-img" src="/plot/{{filename}}.png" />
  </div>
  <div class="pure-u-1-6">
    <h2 class="content-subhead">Ratings</h2>
    <aside id="rating-table-response" class="hidden">
    </aside>

    <table class="pure-table pure-table-bordered">
      <thead>
        <tr>
          <th>Rating</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="rating-table-body">
      </tbody>
    </table>

    <!-- TODO: use a data list for allowed ratings -->
    <form id="rating-new-form" class="pure-form pure-form-aligned">
      <fieldset>
        <input type="text" id="rating-new-text" placeholder="New rating">
      </fieldset>
    </form>
  </div>
</div>

<h2 class="content-subhead">tl;dr</h2>
<pre>
{{repr(flow)}}
</pre>

<script>
  ratingList('{{filename}}');

  var form = document.getElementById('rating-new-form');
  form.addEventListener('submit', function(event) {
    event.preventDefault();

    var rating = document.getElementById('rating-new-text');
    ratingAdd('{{filename}}', rating.value);

    rating.value = '';
  });
</script>

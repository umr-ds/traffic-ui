% rebase('base.tpl', title='Flowdetails', subtitle=filename)

<div class="pure-g">
  <div class="pure-u-1-2"><a class="pure-menu-link" href="/show/{{prec}}">
    <i class="arrow left"></i> Previous
  </a></div>
  <div class="pure-u-1-2"><a class="pure-menu-link" style="text-align: right;" href="/show/{{succ}}">
    Next <i class="arrow right"></i>
  </a></div>
</div>

<div class="pure-g">
  <div class="pure-u-5-6">
    {{!plot}}
  </div>
  <div class="pure-u-1-6">
    <h2 class="content-subhead">Ratings</h2>

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

    <form id="rating-new-form" class="pure-form pure-form-aligned">
      <fieldset>
        <input type="text" id="rating-new-text" />
      </fieldset>
    </form>

    <aside id="rating-table-response" class="hidden">
    </aside>
  </div>
</div>

<h2 class="content-subhead">Detail</h2>
<table class="pure-table pure-table-bordered">
  <tbody>
  % for k,v in flow.html_repr()['meta']:
    <tr>
      <td>{{k}}</td>
      <td>{{v}}</td>
    </tr>
  % end
  </tbody>
</table>

<h3 class="content-subhead">Metrics</h3>
<table class="pure-table pure-table-bordered">
  <thead>
    <tr>
      <th></th>
      <th>Forwards</th>
      <th>Backwards</th>
    </tr>
  </thead>
  <tbody>
  % for t,f,b in flow.html_repr()['metric']:
    <tr>
      <td>{{t}}</td>
      <td>{{f}}</td>
      <td>{{b}}</td>
    </tr>
  % end
  </tbody>
</table>

<script>
  ratingList('{{filename}}');

  var form = document.getElementById('rating-new-form');
  var rating = document.getElementById('rating-new-text');
  var ratings = [ {{!', '.join(['"{}"'.format(r) for r in conf.ratings])}} ];

  form.addEventListener('submit', function(event) {
    event.preventDefault();

    % if conf.enforce:
    if(!ratings.includes(rating.value)) {
      showHint('Undefined rating denied!');
      rating.value = '';

      return;
    }
    % end

    ratingAdd('{{filename}}', rating.value);
    rating.value = '';
  });

  rating.addEventListener('awesomplete-selectcomplete', function(event) {
    ratingAdd('{{filename}}', event.text);
    rating.value = '';
  });

  new Awesomplete(rating, {
    autoFirst: true,
	  list: ratings,
    minChars: 0
  });

  % if conf.plot_backend == 'plotly':
  // Trigger autoscale of the plotly-plot after rendering
  document.querySelector('[data-title="Autoscale"]').click();
  % end
</script>

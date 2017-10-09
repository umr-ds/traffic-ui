% rebase('base.tpl', title='Flowdetails', subtitle=filename)

<img class="pure-img" src="/plot/{{filename}}.png" />

<h2 class="content-subhead">Ratings</h2>
<table class="pure-table pure-table-bordered">
  <thead>
    <tr>
      <th>Rating</th>
    </tr>
  </thead>
  <tbody>
  % for rating in flow.ratings:
  <tr>
    <td>{{rating}}</td>
  </tr>
  % end
  <tbody>
</table>

<h3>Modify</h3>
<!-- TODO: use a data list for allowed ratings -->
<form class="pure-form pure-form-aligned" action="/rating/add/{{filename}}" method="post">
  <input type="text" name="rating" placeholder="New rating">
  <input type="submit" value="Add" class="pure-button pure-button-primary">
</form>

<form class="pure-form pure-form-aligned" action="/rating/del/{{filename}}" method="post">
  <style scoped>
    .button-warning {
      color: white;
      border-radius: 4px;
      text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
      background: rgb(223, 117, 20); /* this is an orange */
    }
  </style>

  <select name="rating" class="pure-input">
    % for rating in flow.ratings:
    <option value="{{rating}}">{{rating}}</option>
    %end
  </select>
  <input type="submit" value="Remove" class="button-warning pure-button">
</form>

<h2 class="content-subhead">tl;dr</h2>
<pre>
{{repr(flow)}}
</pre>

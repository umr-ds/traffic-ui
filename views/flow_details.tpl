<h1>Flowdetails</h1>

<img src="/plot/{{filename}}.png" />

<h2>Ratings</h2>
<ul>
  % for rating in flow.ratings:
  <li>{{rating}}</li>
  % end
</ul>

<!-- TODO: use a data list for allowed ratings -->
<form action="/rating/add/{{filename}}" method="post">
  New rating:
  <input type="text" name="rating">
  <input type="submit" value="Add">
</form>

<form action="/rating/del/{{filename}}" method="post">
  Remove rating:
  <select name="rating">
    % for rating in flow.ratings:
    <option value="{{rating}}">{{rating}}</option>
    %end
  </select>
  <input type="submit" value="Remove">
</form>

<h2>tl;dr</h2>
<pre>
{{repr(flow)}}
</pre>

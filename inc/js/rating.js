function showHint(msg) {
  var respBox = document.getElementById('rating-table-response')
  respBox.innerHTML = '<p>' + msg + '</p>';
  respBox.className = '';

  setTimeout(function() {
    respBox.className = 'hidden';
  }, 1750);
}

function ratingList(filename) {
  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', '/rating/list', true);
  xhttp.setRequestHeader('Content-type', 'application/json');
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var resp = JSON.parse(this.responseText);
      if (resp.status != 'ok')
        return;

      var tbody = document.getElementById('rating-table-body');
      tbody.innerHTML = resp.ratings.map(function(x) {
        return '<tr><td>' + x + '</td><td><button class="pure-button" onclick="ratingRemove(\'' + filename + '\',\'' + x + '\');">Remove</button></td></tr>';
      }).join('');

      if (tbody.innerHTML == '')
        tbody.parentElement.className = 'hidden';
      else
        tbody.parentElement.className = 'pure-table pure-table-bordered';
    }
  };
  xhttp.send('filename=' + filename);
}

function ratingChange(filename, rating, url, msg) {
  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', url, true);
  xhttp.setRequestHeader('Content-type', 'application/json');
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var resp = JSON.parse(this.responseText);
      if (resp.status != 'ok')
        return;

      showHint(msg);

      ratingList(filename);
    }
  };
  xhttp.send('filename=' + filename + '&rating=' + rating);
}

function ratingRemove(filename, rating) {
  ratingChange(filename, rating, '/rating/del', 'Removed!');
}

function ratingAdd(filename, rating) {
  ratingChange(filename, rating, '/rating/add', 'Added!');
}

function overviewTbl(query) {
  var xhttp = new XMLHttpRequest();
  xhttp.open('POST', '/search', true);
  xhttp.setRequestHeader('Content-type', 'application/json');
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var resp = JSON.parse(this.responseText);
      if (resp.status != 'ok')
        return;

      var tbody = document.getElementById('overview-tbl-body');
      tbody.innerHTML = resp.result.map(function(x) {
        var link = '<a class="pure-menu-link" href="/show/' + x.file + '">' + x.file + '</a>';
        var ratings = x.ratings.map(function (x) {
          return '<a href="/#:rating=' + x + '">' + x + '</a>';
        }).join(', ');
        return '<tr><td>' + link + '</td><td>' + ratings + '</td></tr>';
      }).join('');
    }
  };
  xhttp.send('q=' + query);
}

function overviewTblForm() {
  event.preventDefault();

  var txt = document.getElementById('overview-tbl-in').value;
  window.location.hash = '#' + txt;
}

function updateQuery() {
  var input = document.getElementById('overview-tbl-in');
  var query = window.location.hash;

  if (query.charAt(0) == '#') {
    query = query.substr(1);
  }

  input.value = query;
  overviewTbl(query);
}

function searchHistory(awesompleteObj) {
  var xhttp = new XMLHttpRequest();
  xhttp.open('GET', '/search/hist', true);
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      hist = JSON.parse(this.responseText).history;
      awesompleteObj.list = hist.map(function (x) {
        return x.replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#039;");
      });
    }
  };
  xhttp.send();
}

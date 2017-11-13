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
        var ratings = x.ratings.join(', ');
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
  overviewTbl(txt);
}

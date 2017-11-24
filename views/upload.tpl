% rebase('base.tpl', title='Upload', ratings=ratings)

<form class="pure-form pure-form-aligned" action="/upload" method="post" enctype="multipart/form-data">
    <fieldset>
        <div class="pure-control-group">
            <label for="upload">pcap-File</label>
            <input id="upload" type="file" name="upload">
        </div>

        <div class="pure-control-group">
            <label for="password">Password</label>
            <input id="password" type="password" name="password" placeholder="Password">
        </div>

        <div class="pure-controls">
            <button type="submit" class="pure-button pure-button-primary">Upload</button>
        </div>
    </fieldset>
</form>

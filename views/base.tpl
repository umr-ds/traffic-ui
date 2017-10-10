<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrafficUI - {{title}}</title>
    
    <link rel="stylesheet" href="/inc/css/pure-min.css">
    <link rel="stylesheet" href="/inc/css/layouts/side-menu.css">
    <link rel="stylesheet" href="/inc/css/layouts/etc.css">

    <script src="/inc/js/rating.js"></script>
</head>
<body>
<div id="layout">
    <!-- Menu toggle -->
    <a href="#menu" id="menuLink" class="menu-link">
        <!-- Hamburger icon -->
        <span></span>
    </a>

    <div id="menu">
        <div class="pure-menu">
            <a class="pure-menu-heading" href="#">TrafficUI</a>

            <ul class="pure-menu-list">
                <li class="pure-menu-item"><a href="/" class="pure-menu-link">Overview</a></li>
            </ul>
        </div>
    </div>

    <div id="main">
        <div class="header">
            <h1>{{title}}</h1>
            % if defined('subtitle'):
            <h2>{{subtitle}}</h2>
            % end
        </div>

        <div class="content">
          {{!base}}
        </div>
    </div>
</div>

<script src="/inc/js/ui.js"></script>
</body>
</html>

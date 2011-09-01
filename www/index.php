<!DOCTYPE html>
<html>

	<head>
		<meta charset="utf-8"/>
		<title>LibraryD&aelig;mon | hami.sh labs</title>
		<!--[if lt IE 9]>
			<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
		<![endif]-->
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js"></script>
		<script src="js/jquery.tablesorter.min.js"></script>
		<script>
			$(document).ready(function() 
			    { 
			    	$("#checkouts table").tablesorter( {sortList: [[1,0]]} ); 
			    } 
			);
		</script>
		<link rel="stylesheet" media="all" href="css/library.css"/>
		<meta name="viewport" content="width=device-width, initial-scale=1"/>
		<!-- Adding "maximum-scale=1" fixes the Mobile Safari auto-zoom bug: http://filamentgroup.com/examples/iosScaleBug/ -->
	</head>
	
	<body lang="en">
		<header id="masthead">
			<h1>LibraryD&aelig;mon</h1>
		</header>
		<section id="checkouts">
			
			<table>
				<thead>
					<tr>
						<th class="item">Title</th>
						<th class="due">Due</th>
						<th class="status">Status</th>
					</tr>
				</thead>
				<tbody>
				<?php
					include("inc/_books.inc.php");
				?>
				</tbody>
				
			</table>
			
			<?php
				include("inc/_account.inc.php");
			?>
			
		</section>
		<footer>
			<?
				$last_modified = filemtime("inc/_books.inc.php");
				$last_modified = date("m/j/y h:i", $last_modified);
			?>
			<p>&copy; <a href="http://hami.sh/">hamish</a> | last updated <?=$last_modified?></p>
		</footer>
	</body>
	
</html>
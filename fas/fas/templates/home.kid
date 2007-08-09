<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'master.kid'">
<head>
  <title>Fedora Accounts System</title>
</head>
<body>

<h2 py:if="'userID' in builds.userLink" class="accounts">Recent Builds <a href='${builds.userLink}'>(Koji)</a></h2>
<table py:if="'userID' in builds.userLink">
    <thead>
        <tr><th>Build</th><th>Build Date</th></tr>
    </thead>
    <!--<tr><td>Koji</td><td><a href='${builds.userLink}'>Build Info</a></td></tr>-->
    <tr py:for="build in builds.builds">
        <td>
          <span py:if="'complete' in builds.builds[build]['title']" class="approved"><a href="${build}">${builds.builds[build]['title']}</a></span>
          <span py:if="'failed' in builds.builds[build]['title']" class="unapproved"><a href="${build}">${builds.builds[build]['title']}</a></span>
        </td>
        <td>${builds.builds[build]['pubDate']}</td>
    </tr>
</table>

</body>
</html>

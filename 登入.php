<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>喝ㄉㄟˇㄉㄟˊ登入</title>
<link href="login.css" type="text/css" rel="stylesheet" />

<style>
   @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@700;900&family=Rubik+Wet+Paint&family=Tapestry&display=swap');

   body {
      font-family: 'Noto Serif TC', serif;
    }

   h1 a {
      font-family: 'Noto Serif TC', serif;
   }
</style>


<h1 style="background-color: #147643;">
   <a name="title">喝ㄉㄟˇㄉㄟˊ</a>
</h1>
<center>
<?php
if (isset($_POST["button"])) {
session_start();  
$username = "";  $password = "";
if ( isset($_POST["username"]) ){
   $username = $_POST["username"];
   $_SESSION['username']=$_POST['username'];}
if ( isset($_POST["password"]) )
   $password = $_POST["password"];
if ($username != "" && $password != "") {
   $link = mysqli_connect("localhost","root",
                          "123","drink tea")
        or die("無法開啟MySQL資料庫連接!<br/>");
   $sql = "SELECT * FROM customer WHERE password='".$password."' AND username='".$username."'";
   $result = mysqli_query($link, $sql);
   $total_records = mysqli_num_rows($result);
   if ( $total_records > 0 ) {
      $_SESSION["login_session"] = true;
      if($username=="admin"){
        header("Location: 商品資料.php");
      } else{
         header("Location: 商品介紹.php");
      }
   } else {  
      echo "<font color='red'>";
      echo "使用者名稱或密碼錯誤!<br/>";
      echo "</font>";
      $_SESSION["login_session"] = false;
   }
   mysqli_close($link);    
}else{
   echo "<font color='red'>";
   echo "使用者名稱或密碼空白!<br/>";
   echo "</font>";
   $_SESSION["login_session"] = false;
}
}
?></center>
</head>
<body>
<div style="margin-top: 13%; text-align:center;">
<a name="signin"href="會員新增.php">會員註冊</a>
<a name="login" href="會員登入.php">會員登入</a>
<form  action = "會員登入.php" method = "post">  
<p>帳號：<input type="text" name="username" style="border-radius: 10px; font-size: 20px;" size="15"/></p>
<p>密碼：<input type="password" name="password" style="border-radius: 10px; font-size: 20px;" size="15"/></p> 
<input type="submit" name="button" style="font-family: 'Noto Serif TC', serif; border:none;
    background-color: #147643; border-radius: 10px; color:white; padding: 8px 15px; " value="登入"/>
</form>
</div>
</body>
</html>
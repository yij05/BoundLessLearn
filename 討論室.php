<?php
// 設置資料庫連線
$host = 'localhost';
$dbname = 'discussion_room';
$username = 'root';
$password = '';
$pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);

// 設定 CORS 和 JSON 輸出
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// API 路由邏輯
$method = $_SERVER['REQUEST_METHOD'];
$request = explode('/', trim($_SERVER['PATH_INFO'], '/'));

switch ($method) {
    case 'POST':
        if ($request[0] == 'auth' && $request[1] == 'register') {
            registerUser($pdo);
        } elseif ($request[0] == 'auth' && $request[1] == 'login') {
            loginUser($pdo);
        } elseif ($request[0] == 'rooms' && $request[1] == 'create') {
            createRoom($pdo);
        } elseif ($request[0] == 'rooms' && isset($request[2]) && $request[2] == 'messages') {
            sendMessage($pdo, $request[1]);
        } elseif ($request[0] == 'rooms' && isset($request[2]) && $request[2] == 'upload') {
            uploadImage($pdo, $request[1]);
        }
        break;
    
    case 'GET':
        if ($request[0] == 'rooms' && isset($request[1])) {
            getMessages($pdo, $request[1]);
        }
        break;
}

function registerUser($pdo) {
    $data = json_decode(file_get_contents("php://input"), true);
    $username = $data['username'];
    $email = $data['email'];
    $password = password_hash($data['password'], PASSWORD_BCRYPT);

    $stmt = $pdo->prepare("INSERT INTO users (username, email, password) VALUES (?, ?, ?)");
    if ($stmt->execute([$username, $email, $password])) {
        echo json_encode(['message' => 'User registered successfully!']);
    } else {
        echo json_encode(['message' => 'Registration failed.']);
    }
}

function loginUser($pdo) {
    $data = json_decode(file_get_contents("php://input"), true);
    $email = $data['email'];
    $password = $data['password'];

    $stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $user = $stmt->fetch();

    if ($user && password_verify($password, $user['password'])) {
        echo json_encode(['message' => 'Login successful!', 'user_id' => $user['id']]);
    } else {
        echo json_encode(['message' => 'Invalid credentials.']);
    }
}

function createRoom($pdo) {
    $data = json_decode(file_get_contents("php://input"), true);
    $roomName = $data['room_name'];
    $isPrivate = isset($data['is_private']) ? $data['is_private'] : false;
    $inviteCode = isset($data['invite_code']) ? $data['invite_code'] : null;
    $createdBy = $data['created_by'];

    $stmt = $pdo->prepare("INSERT INTO rooms (room_name, is_private, invite_code, created_by) VALUES (?, ?, ?, ?)");
    if ($stmt->execute([$roomName, $isPrivate, $inviteCode, $createdBy])) {
        echo json_encode(['message' => 'Room created successfully!']);
    } else {
        echo json_encode(['message' => 'Room creation failed.']);
    }
}

function sendMessage($pdo, $roomId) {
    $data = json_decode(file_get_contents("php://input"), true);
    $userId = $data['user_id'];
    $content = $data['content'];

    $stmt = $pdo->prepare("INSERT INTO messages (room_id, user_id, content, type) VALUES (?, ?, ?, 'text')");
    if ($stmt->execute([$roomId, $userId, $content])) {
        echo json_encode(['message' => 'Message sent successfully!']);
    } else {
        echo json_encode(['message' => 'Message sending failed.']);
    }
}

function uploadImage($pdo, $roomId) {
    if (isset($_FILES['image'])) {
        $fileTmpPath = $_FILES['image']['tmp_name'];
        $fileName = $_FILES['image']['name'];
        $fileNameCmps = explode(".", $fileName);
        $fileExtension = strtolower(end($fileNameCmps));
        $uploadFileDir = './uploads/';
        $dest_path = $uploadFileDir . $fileName;

        $allowedfileExtensions = array('jpg', 'gif', 'png', 'jpeg');
        if (in_array($fileExtension, $allowedfileExtensions)) {
            if (move_uploaded_file($fileTmpPath, $dest_path)) {
                $imageUrl = $dest_path;
                $userId = $_POST['user_id'];

                $stmt = $pdo->prepare("INSERT INTO messages (room_id, user_id, image_url, type) VALUES (?, ?, ?, 'image')");
                if ($stmt->execute([$roomId, $userId, $imageUrl])) {
                    echo json_encode(['message' => 'Image uploaded successfully!']);
                } else {
                    echo json_encode(['message' => 'Image upload failed.']);
                }
            } else {
                echo json_encode(['message' => 'There was some error moving the file.']);
            }
        } else {
            echo json_encode(['message' => 'File type not allowed.']);
        }
    } else {
        echo json_encode(['message' => 'No image uploaded.']);
    }
}

function getMessages($pdo, $roomId) {
    $stmt = $pdo->prepare("SELECT * FROM messages WHERE room_id = ?");
    $stmt->execute([$roomId]);
    $messages = $stmt->fetchAll(PDO::FETCH_ASSOC);

    echo json_encode($messages);
}

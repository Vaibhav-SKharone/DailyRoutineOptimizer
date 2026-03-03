// =============================
// REGISTER FUNCTION
// =============================
function register() {
    let users = JSON.parse(localStorage.getItem("users")) || [];

    let user = {
        username: document.getElementById("regUsername").value,
        password: btoa(document.getElementById("regPassword").value), // basic encryption
        role: document.getElementById("regRole").value
    };

    users.push(user);
    localStorage.setItem("users", JSON.stringify(users));

    alert("Registered Successfully!");
}

// =============================
// LOGIN FUNCTION
// =============================
function login() {
    let users = JSON.parse(localStorage.getItem("users")) || [];

    let username = document.getElementById("loginUsername").value;
    let password = btoa(document.getElementById("loginPassword").value);

    let user = users.find(u => u.username === username && u.password === password);

    if (user) {
        localStorage.setItem("currentUser", JSON.stringify(user));

        if (user.role === "admin") {
            window.location = "admin.html";
        } else {
            window.location = "dashboard.html";
        }
    } else {
        alert("Invalid Credentials!");
    }
}

// =============================
// ADD TASK FUNCTION
// =============================
function addTask() {
    let tasks = JSON.parse(localStorage.getItem("tasks")) || [];

    let task = {
        name: document.getElementById("taskName").value,
        priority: document.getElementById("priority").value,
        duration: document.getElementById("duration").value,
        deadline: document.getElementById("deadline").value,
        category: document.getElementById("category").value,
        completed: false,
        createdDate: new Date().toISOString()
    };

    tasks.push(task);

    // Intelligent Sorting: Priority first, then Deadline
    tasks.sort((a, b) =>
        a.priority - b.priority ||
        new Date(a.deadline) - new Date(b.deadline)
    );

    localStorage.setItem("tasks", JSON.stringify(tasks));

    displayTasks();
}

// =============================
// DISPLAY TASKS
// =============================
function displayTasks() {
    let tasks = JSON.parse(localStorage.getItem("tasks")) || [];
    let list = document.getElementById("taskList");

    if (!list) return;

    list.innerHTML = "";

    tasks.forEach((task, index) => {
        let li = document.createElement("li");

        li.innerHTML =
            task.name +
            " | Priority: " + task.priority +
            " | Deadline: " + task.deadline +
            " | Category: " + task.category +
            (task.completed ? " ✅" : "") +
            " <button onclick='completeTask(" + index + ")'>Done</button>";

        list.appendChild(li);
    });

    updateScore();
    weeklySummary();
}

// =============================
// COMPLETE TASK
// =============================
function completeTask(index) {
    let tasks = JSON.parse(localStorage.getItem("tasks")) || [];
    tasks[index].completed = true;
    localStorage.setItem("tasks", JSON.stringify(tasks));

    displayTasks();
}

// =============================
// PRODUCTIVITY SCORE
// =============================
function updateScore() {
    let tasks = JSON.parse(localStorage.getItem("tasks")) || [];

    let completed = tasks.filter(t => t.completed).length;
    let total = tasks.length;

    let score = total === 0 ? 0 : (completed / total) * 100;

    let scoreElement = document.getElementById("score");

    if (scoreElement) {
        scoreElement.innerText =
            "Productivity Score: " + score.toFixed(2) + "%";
    }
}

// =============================
// WEEKLY SUMMARY FUNCTION
// =============================
function weeklySummary() {
    let tasks = JSON.parse(localStorage.getItem("tasks")) || [];

    let now = new Date();
    let weekAgo = new Date();
    weekAgo.setDate(now.getDate() - 7);

    let weeklyTasks = tasks.filter(task =>
        new Date(task.createdDate) >= weekAgo
    );

    let total = weeklyTasks.length;
    let completed = weeklyTasks.filter(t => t.completed).length;
    let pending = total - completed;

    let percentage = total === 0 ? 0 : (completed / total) * 100;

    let stats = document.getElementById("weeklyStats");

    if (stats) {
        stats.innerHTML =
            "Total Tasks: " + total + "<br>" +
            "Completed: " + completed + "<br>" +
            "Pending: " + pending + "<br>" +
            "Weekly Productivity: " + percentage.toFixed(2) + "%";
    }

    drawChart(completed, pending);
}

// =============================
// DRAW BAR CHART
// =============================
function drawChart(completed, pending) {
    let canvas = document.getElementById("weeklyChart");
    if (!canvas) return;

    let ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let maxHeight = 150;

    let completedHeight = completed * 20;
    let pendingHeight = pending * 20;

    ctx.fillStyle = "#4CAF50";
    ctx.fillRect(60, maxHeight - completedHeight, 50, completedHeight);

    ctx.fillStyle = "#F44336";
    ctx.fillRect(160, maxHeight - pendingHeight, 50, pendingHeight);

    ctx.fillStyle = "#000";
    ctx.fillText("Completed", 55, 170);
    ctx.fillText("Pending", 165, 170);
}

// =============================
// ADMIN PANEL USER DISPLAY
// =============================
if (window.location.pathname.includes("admin.html")) {
    let users = JSON.parse(localStorage.getItem("users")) || [];
    let list = document.getElementById("userList");

    if (list) {
        users.forEach(user => {
            let li = document.createElement("li");
            li.innerText = user.username + " - " + user.role;
            list.appendChild(li);
        });
    }
}

// =============================
// AUTO LOAD ON PAGE OPEN
// =============================
displayTasks();
weeklySummary();
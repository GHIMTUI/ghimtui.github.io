const express = require("express");
const app = express();

app.get("/", (req, res) => {
  res.send("Server Node.js đang chạy trên Render!");
});

app.listen(10000, () => console.log("Server đang chạy ở cổng 10000"));

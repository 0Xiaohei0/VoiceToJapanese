const express = require("express");
const app = express();
const port = 3000;

const CharacterAI = require("node_characterai");
const characterAI = new CharacterAI();

(async () => {
  await characterAI.authenticateAsGuest();

  const characterId = "Lzx1xsokHaJNKf5EP20kNGcfSrXJM30Uhez8z9DaOXw"; // Yoimiya 0v0

  const chat = await characterAI.createOrContinueChat(characterId);
  const response = await chat.sendAndAwaitResponse("Do you know paimon?", true);

  console.log(response);
  // use response.text to use it in a string.
})();

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});

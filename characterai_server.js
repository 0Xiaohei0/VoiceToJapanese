const express = require("express");
const app = express();
const port = 3000;

const CharacterAI = require("node_characterai");
const characterAI = new CharacterAI();
chat = null;

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

app.post("/authenticate", async (req, res) => {
  try {
    await characterAI.authenticateAsGuest();
    res.status(200).send("Authentication successful");
  } catch (error) {
    print(error);
    res.status(500).send("Error occurred during authentication");
  }
});

app.post("/setCharacter", async (req, res) => {
  try {
    chat = await characterAI.createOrContinueChat(characterId);
    res.status(200).send("Chat creation successful");
  } catch (error) {
    print(error);
    res.status(500).send("Error occurred during chat creation");
  }
});

app.get("/sendChat", async (req, res) => {
  try {
    const response = await chat.sendAndAwaitResponse(
      "Do you know paimon?",
      true
    );
    res.status(200).send(response);
  } catch (error) {
    print(error);
    res.status(500).send("Error sending chat");
  }
});

app.listen(port, () => {
  console.log(`character_ai wrapper listening on port ${port}`);
});

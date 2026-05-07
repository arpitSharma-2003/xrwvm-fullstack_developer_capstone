/*jshint esversion: 8 */

const express = require("express");
const mongoose = require("mongoose");
const fs = require("fs");
const cors = require("cors");

const Cars = require("./inventory");

const app = express();
const port = 3050;

app.use(cors());
app.use(express.json());
const raw = JSON.parse(fs.readFileSync("./data/car_records.json", "utf8"));
const cars_data = raw.cars;

// Connect to MongoDB inside docker-compose (service name mongo_db)
mongoose.connect("mongodb://mongo_db:27017/", { dbName: "carsInventoryDB" });

mongoose.connection.on("connected", async () => {
  try {
    // Load data into DB (idempotent reset for lab)
    await Cars.deleteMany({});
    await Cars.insertMany(cars_data);
    console.log("Cars data loaded into MongoDB");
  } catch (err) {
    console.log("Error loading cars data:", err);
  }
});

// Root endpoint
app.get("/", async (req, res) => {
  res.send("Welcome to the Mongoose API");
});

// 1) cars/:id  (dealer id)
app.get("/cars/:id", async (req, res) => {
  try {
    const documents = await Cars.find({ dealer_id: Number(req.params.id) });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching documents" });
  }
});

// 2) carsbymake/:id/:make
app.get("/carsbymake/:id/:make", async (req, res) => {
  try {
    const documents = await Cars.find({
      dealer_id: Number(req.params.id),
      make: req.params.make,
    });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching documents" });
  }
});

// 3) carsbymodel/:id/:model
app.get("/carsbymodel/:id/:model", async (req, res) => {
  try {
    const documents = await Cars.find({
      dealer_id: Number(req.params.id),
      model: req.params.model,
    });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching documents" });
  }
});

// Helper for mileage bands
function mileageQuery(mileageBand) {
  const m = Number(mileageBand);

  if (m <= 50000) return { $lte: 50000 };
  if (m <= 100000) return { $gte: 50000, $lte: 100000 };
  if (m <= 150000) return { $gte: 100000, $lte: 150000 };
  if (m <= 200000) return { $gte: 150000, $lte: 200000 };
  return { $gte: 200000 };
}

// 4) carsbymaxmileage/:id/:mileage
app.get("/carsbymaxmileage/:id/:mileage", async (req, res) => {
  try {
    const mileageFilter = mileageQuery(req.params.mileage);
    const documents = await Cars.find({
      dealer_id: Number(req.params.id),
      mileage: mileageFilter,
    });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching documents" });
  }
});

// Helper for price bands
function priceQuery(priceBand) {
  const p = Number(priceBand);

  if (p <= 20000) return { $lte: 20000 };
  if (p <= 40000) return { $gte: 20000, $lte: 40000 };
  if (p <= 60000) return { $gte: 40000, $lte: 60000 };
  if (p <= 80000) return { $gte: 60000, $lte: 80000 };
  return { $gte: 80000 };
}

// 5) carsbyprice/:id/:price
app.get("/carsbyprice/:id/:price", async (req, res) => {
  try {
    const priceFilter = priceQuery(req.params.price);
    const documents = await Cars.find({
      dealer_id: Number(req.params.id),
      price: priceFilter,
    });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching documents" });
  }
});

// 6) carsbyyear/:id/:year  (minimum year)
app.get("/carsbyyear/:id/:year", async (req, res) => {
  try {
    const documents = await Cars.find({
      dealer_id: Number(req.params.id),
      year: { $gte: Number(req.params.year) },
    });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching documents" });
  }
});

app.listen(port, () => {
  console.log(`Cars Inventory API running on http://localhost:${port}`);
});
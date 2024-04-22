const exerciseLabel = document.getElementById('exercise-label');
const repsLabel = document.getElementById('reps-label');
const durationLabel = document.getElementById('duration-label');
const calorieLabel = document.getElementById('calories-label');
const addLogBtn = document.getElementById('add-log');

let cardData = [];

const saveToLocalStorage = function () {
   localStorage.setItem('fitify', JSON.stringify(cardData));
};

const getFromLocalStorage = function () {
   const localStorageData = JSON.parse(localStorage.getItem('fitify'));

   if (!localStorageData) return;

   localStorageData.forEach((data) => cardData.push(data));
};

getFromLocalStorage();

const USER_WEIGHT_KG = 50;

function calculateCalorie(data) {
   const metValues = {
      'barbell biceps curl': 3.5,
      'bench press': 3.5,
      'chest fly machine': 3.0,
      deadlift: 4.5,
      'decline bench press': 3.5,
      'hammer curl': 3.0,
      'hip thrust': 3.0,
      'incline bench press': 3.5,
      'lat pulldown': 3.5,
      'lateral raises': 3.5,
      'leg extension': 3.0,
      'leg raises': 4.5,
      plank: 3.3,
      'pull up': 8.0,
      'push up': 8.0,
      'romanian deadlift': 4.5,
      'russian twist': 4.5,
      'shoulder press': 4.0,
      squat: 5.0,
      't bar row': 5.0,
      'tricep dips': 4.0,
      'tricep pushdown': 3.0,
   };

   const met = metValues[data.exercise];

   const durationHours = ((Date.now() - new Date(data.duration)) / (1000 * 60) + 330) / 60;

   // MET * weight (kg) * duration (hours)
   const caloriesBurned = met * USER_WEIGHT_KG * durationHours;

   return caloriesBurned ? caloriesBurned.toFixed(2) : 0;
}

function updateExercise(data) {
   exerciseLabel.innerText = data.exercise || 'start!!';
   repsLabel.innerText = data.rep || 0;
   durationLabel.innerHTML = ((Date.now() - new Date(data.duration)) / (1000 * 60) + 330).toFixed(2) || 0;
   calorieLabel.innerHTML = calculateCalorie(data) || 0;
}

function addWorkoutLog(data) {
   if (data.rep != 0) {
      cardData.push({
         timestamp: Date.now(),
         type: data.exercise,
         duration: ((Date.now() - new Date(data.duration)) / (1000 * 60) + 330).toFixed(2),
         reps: data.rep,
         calories: calculateCalorie(data) || 0,
      });

      saveToLocalStorage();
      window.location.href = '/';
   } else {
      window.alert("You haven't done any workout. Yet you are quitting 🤨");
   }
}

function fetchRecognizedExercise() {
   fetch('/get_exercise')
      .then((response) => response.json())
      .then((data) => {
         updateExercise(data);
      })
      .catch((error) => {
         console.error('Error fetching recognized exercise:', error);
      });
}

// Call fetchRecognizedExercise initially
fetchRecognizedExercise();

// Set an interval to fetch the recognized exercise every 1 second
setInterval(fetchRecognizedExercise, 1000);

addLogBtn.addEventListener('click', () => {
   fetch('/get_exercise')
      .then((response) => response.json())
      .then((data) => {
         addWorkoutLog(data);
      })
      .catch((error) => {
         console.error('Error fetching recognized exercise:', error);
      });
});

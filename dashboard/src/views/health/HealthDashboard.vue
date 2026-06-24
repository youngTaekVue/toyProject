<template>
  <div class="health-dashboard">
    <h1>Health Dashboard</h1>
    <p>Fetching Google Fit data...</p>
    <div v-if="googleFitData.length > 0">
      <h2>Google Fit Data:</h2>
      <ul>
        <li v-for="(item, index) in googleFitData" :key="index">{{ item.message }}</li>
      </ul>
    </div>
    <div v-else>
      <p>No Google Fit data available yet.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HealthDashboard',
  data() {
    return {
      googleFitData: [],
    };
  },
  async mounted() {
    console.log('HealthDashboard mounted. Attempting to fetch Google Fit data...'); // 추가된 로그
    try {
      const response = await axios.get('http://localhost:3000/health/google-fit/auth'); // Assuming your backend runs on port 3000
      this.googleFitData = response.data.data;
      console.log('Google Fit Data fetched successfully:', this.googleFitData); // 수정된 로그
    } catch (error) {
      console.error('Error fetching Google Fit data:', error);
    }
  },
};
</script>

<style scoped>
.health-dashboard {
  padding: 20px;
  font-family: Arial, sans-serif;
}
h1 {
  color: #333;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  background-color: #f0f0f0;
  margin-bottom: 5px;
  padding: 10px;
  border-radius: 5px;
}
</style>
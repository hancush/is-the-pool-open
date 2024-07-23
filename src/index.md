---
theme: [glacier, wide]
title: Is The Pool Open????
toc: false
sidebar: false
---

<style type="text/css">
  h2, h3 {
    margin-bottom: 0;
  }

  ul {
    padding-left: 20px;
  }

  .featured-result h2 {
    font-size: 20pt;
  }

  .featured-result {
    font-size: 125%;
  }
</style>


<div align="center">
  <table>
    <tr>
      <td style="font-size: 20pt;" align="center">
        💦💦💦💦<br />
        <span style="color: red; font-size: 20pt;">✶ ✶ ✶ ✶</span><br />
        💦💦💦💦
      </td>
      <td style="vertical-align: middle;">
        <h1>Is The Pool Open????</h1>
        <em>Find an open Chicago Park District pool near you!</em>
      </td>
    </tr>
  </table>
</div>

```js
const turf = import("npm:@turf/turf@7");
const pools = FileAttachment("data/pools.json").json({typed: true});
```

```js
const days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

const now = new Date()

const getWeekday = function(date) {
  return days_of_week[date.getDay()]
}

const scheduleOn = function(pool, weekday) {
  if (Object.keys(pool.schedule).length > 0) {
    return pool.schedule[weekday]
  }
}

const isOpen = function(pool, weekday = getWeekday(now), time = now) {
  if ( !weekday ) {
    return Object.keys(pool.schedule).length > 0
  }
  const schedule = scheduleOn(pool, weekday)
  if (schedule) {
    return time
      ? schedule.open < time.toTimeString() && time.toTimeString() < schedule.close
      : schedule.open && schedule.close
  }
}

const getPoolDetailString = function(pool, weekday) {
  let scheduleStr = htl.html``
  if ( weekday ) {
    const schedule = scheduleOn(pool, weekday)
    scheduleStr = htl.html`Open on ${weekday} from ${schedule.open} to ${schedule.close}<br />`
  } else {
    scheduleStr = htl.html`<ul>
      ${Object.keys(pool.schedule).map((day) => 
      htl.html`<li><strong>${day}:</strong> ${Object.keys(pool.schedule[day]).length > 0 
        ? `${pool.schedule[day].open} to ${pool.schedule[day].close}` 
        : "Closed"}`
      )}
    </ul>`
  }

  return htl.html`
    <h2>${pool.name} <small>${pool.address}</small></h2>
    ${pool.distance ? htl.html`<em>${Math.round(pool.distance)} mile${pool.distance > 1 ? `s` : ``} away</em>` : ``}
    ${pool.alert && htl.html`<p style="color: red; font-weight: bold;">🚨 ${pool.alert} 🚨</p>`}
    <p>
      ${scheduleStr}
      ${pool.schedule_pdf_urls.length > 0
        ? htl.html`<br /><a href=${pool.schedule_pdf_urls[0]} target="_blank">View schedule &raquo;</a><br />`
        : ``
      }
      <a href=${pool.url} target="_blank">View on Parks District website &raquo;</a>
    </p>`
}
```

```js
// https://observablehq.com/@pierreleripoll/geocoding-nominatim
const geocode = function(address, geo_bounds = [[-88.262827,41.47017],[-87.523432,42.153981]], number_result = 1) {
  let viewbox = geo_bounds && geo_bounds[0] && geo_bounds[1]
      ? `&viewbox=${geo_bounds[0][0]},${geo_bounds[0][1]},${geo_bounds[1][0]},${geo_bounds[1][1]}&bounded=1`
      : "";
  return fetch(
    `https://nominatim.openstreetmap.org/search?q=${address}&format=json&limit=${number_result}${viewbox}`,
    { referrer: "https://observablehq.com/@pierreleripoll/geocoding-nominatim" }
  )
}
```

```js
const selectedTime = view(Inputs.radio(
  new Map([
    ["All Pools", null], 
    ["Open Now", now]
  ]), {label: "Filter", value: null})
);
```

```js
const selectedLocation = view(Inputs.radio(
  new Map([
    ["Any pool location", null],
    ["Indoors", "indoor"], 
    ["Outdoors", "outdoor"]
  ]), {label: "Pool location", value: null})
);
```

```js
const selectedWeekday = view(Inputs.select(
  new Map([
    ["Any day", null]].concat(
      days_of_week.map((weekday) => [weekday, weekday])
    )
  ), {value: getWeekday(now), label: "Open on", disabled: Boolean(selectedTime)}));
```

```js

```

```js
const address = view(
  Inputs.text({
    label: "Nearest to",
    placeholder: "Enter an address",
    value: null,
    submit: true
  })
);
```

```js
const position = address ? new Promise((resolve) => {
  geocode(address)
    .then((response) => response.json())
    .then((data) => resolve(data[0]))
}) : null;
```

```js
const div = display(document.createElement("div"));
div.style = "height: 400px;";

const map = L.map(div);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
})
  .addTo(map);

let selectedPoolsOnDay = pools.filter((pool) => {
  if ( isOpen(pool, selectedWeekday, selectedTime) ) {
    return selectedLocation ? pool.location[selectedLocation] : pool
  }
});

let markers = []
let nearestPool
let nearestPoolMarker

if (address) {
  const positionPoint = turf.point([position.lon, position.lat])
  selectedPoolsOnDay = selectedPoolsOnDay.map((pool) => {
    const poolPoint = turf.point([pool.lon, pool.lat], pool)
    return {
      ...pool,
      distance: turf.distance(positionPoint, poolPoint, {units: "miles"})
    }
  }).sort((a, b) => a.distance - b.distance)

  nearestPool = selectedPoolsOnDay[0]

  markers.push(L.marker([position.lat, position.lon]).addTo(map)
    .bindPopup(`<h3>${address}</h3>`)
  );

  nearestPoolMarker = L.circleMarker([
    nearestPool.lat, 
    nearestPool.lon
  ], {
    color: isOpen(nearestPool) ? 'green' : 'gray',
    radius: 10
  }).addTo(map)
    .bindPopup(getPoolDetailString(nearestPool, selectedWeekday));
  
  markers.push(nearestPoolMarker);
} else {
  selectedPoolsOnDay.sort((a, b) => a.name.localeCompare(b.name)).map((pool) => {
    const marker = L.circleMarker([pool.lat, pool.lon], {
      color: isOpen(pool) ? 'green' : 'gray',
      radius: 5,
    }).addTo(map)
      .bindPopup(getPoolDetailString(pool, selectedWeekday));
    markers.push(marker);
  });
}

var markerGroup = new L.featureGroup(markers);

position
  ? map.fitBounds(markerGroup.getBounds(), {padding: [50, 50]})
  : map.setView([41.81, -87.6298], 10);

nearestPool
  ? nearestPoolMarker.openPopup()
  : () => {}
```

```js
const featuredResult = nearestPool ? htl.html`
  <h3>Nearest result to '${address}'</h3>
  <div class="card featured-result">
    ${getPoolDetailString(nearestPool, selectedWeekday)}
  </div>
` : ``

const resultGrid = htl.html`
  <h3>All results</h3>
  <div class="grid grid-cols-3" id="selected-pools">
    ${selectedPoolsOnDay.map((pool) => htl.html`<div class="card">${getPoolDetailString(pool, selectedWeekday)}</div>`)}
    ${selectedPoolsOnDay.length == 0 ? htl.html`<p><em>No pools meet selected criteria, womp womp 😢</em></p>` : ``}
  </div>
`

const results = htl.html`${featuredResult}${resultGrid}`

display(results)
```

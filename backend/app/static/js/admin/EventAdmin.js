function copyDateStartValue() {
  function fieldClickHandler(elem) {
    const dateValue = document.querySelector("#id_date_start").value;
    if (elem.target.value === "") {
      elem.target.value = dateValue;
    }
  }

  const fields = document.querySelectorAll("input[id^='id_races']");
  fields.forEach((f) => {
    if (f.attributes["id"].value.indexOf("date") > 0) {
      console.log("add listener");
      f.addEventListener("focus", fieldClickHandler);
    }
  });

  document
    .getElementById("id_date_end")
    .addEventListener("focus", fieldClickHandler);
}

window.onload = copyDateStartValue;

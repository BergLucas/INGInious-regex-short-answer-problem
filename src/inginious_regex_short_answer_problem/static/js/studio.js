/**
 * Init a regex short answer template
 * @param well: the DOM element containing the input fields
 * @param pid
 * @param problem
 */
function studio_init_template_regex_short_answer(well, pid, problem) {
  if ("centralize" in problem && problem["centralize"])
    $("#centralize-" + pid, well).attr("checked", true);

  var no_match_message = "";
  if ("no_match_message" in problem)
    no_match_message = problem["no_match_message"];

  registerCodeEditor($("#no_match_message-" + pid)[0], "rst", 1).setValue(
    no_match_message
  );

  jQuery.each(problem["matches"], function (index, elem) {
    studio_create_regex_short_answer_match(pid, elem);
  });
}

/**
 * Create a new match in a given regex short answer problem
 * @param pid
 * @param match_data
 */
function studio_create_regex_short_answer_match(pid, match_data) {
  var well = $(studio_get_problem(pid));

  var index = 0;
  while ($("#regex-" + pid + "-" + index).length != 0) index++;

  var row = $("#subproblem_regex_short_answer_matches").html();
  var new_row_content = row.replace(/PID/g, pid).replace(/MATCH/g, index);
  var new_row = $("<div></div>")
    .attr("id", "regex-" + index + "-" + pid)
    .html(new_row_content);
  $("#matches-" + pid, well).append(new_row);

  if ("regex" in match_data) {
    $(".subproblem_regex_short_answer_regex", new_row).val(match_data["regex"]);
  }

  var feedback = "";
  if ("feedback" in match_data) feedback = match_data["feedback"];

  registerCodeEditor(
    $(".subproblem_regex_short_answer_feedback", new_row)[0],
    "rst",
    1
  ).setValue(feedback);

  if ("valid" in match_data && match_data["valid"] == true) {
    studio_toggle_regex_short_answer_match(
      $(".subproblem_regex_short_answer_valid", new_row).attr("name")
    );
  }
}

/**
 * Toggle regex short answer match valid field
 * @param input_name Name of the checkbox input
 */
function studio_toggle_regex_short_answer_match(input_name) {
  var checkbox = $("input[name='" + input_name + "']");
  checkbox.click();
  var btn = checkbox.next("button");
  btn.toggleClass("btn-danger");
  btn.toggleClass("btn-success");
  var icon = btn.find("i");
  icon.toggleClass("fa-times");
  icon.toggleClass("fa-check");
}

/**
 * Delete a regex short answer match
 * @param pid
 * @param match
 */
function studio_delete_regex_short_answer_match(pid, match) {
  $("#regex-" + match + "-" + pid).detach();
}

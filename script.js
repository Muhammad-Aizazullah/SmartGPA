
const apiUrl = "http://127.0.0.1:8000";

async function addCourse() {
    const course = document.getElementById("course")?.value.trim();
    const credit = parseInt(document.getElementById("credit")?.value);
    const grade = document.getElementById("grade")?.value;

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ course, credit, grade }),
    });

    const result = await response.json();
    if (response.ok) {
        alert(result.message);
        updateCourseList();
    } else {
        alert(result.error || 'Failed to add course.');
    }
}

async function updateCourseList() {
    const response = await fetch(apiUrl);
    const courses = await response.json();

    const courseList = document.getElementById('courseList');
    courseList.innerHTML = '';

    courses.forEach(course => {
        const li = document.createElement('li');
        li.textContent = 
`${course.course_name} - Credits: ${course.credit_hours}, Grade: ${course.grade}`;
        courseList.appendChild(li);
    });

    const gpaResponse = await fetch(`${apiUrl}/gpa`);
    const gpaData = await gpaResponse.json();
    document.getElementById('gpaDisplay').textContent = `GPA: ${gpaData.gpa.toFixed(2)}`;
}

function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.classList.toggle('hidden');
}

function calculateRequiredGPA() {
    const currentGPA = parseFloat(document.getElementById("currentGPA").value);
    const targetGPA = parseFloat(document.getElementById("targetGPA").value);
    const currentCredits = parseInt(document.getElementById("currentCredits").value);
    const additionalCredits = parseInt(document.getElementById("additionalCredits").value);

    const totalCredits = currentCredits + additionalCredits;
    const requiredGPA = ((targetGPA * totalCredits) - (currentGPA * currentCredits)) / additionalCredits;

    alert(`Required GPA in additional credits: ${requiredGPA.toFixed(2)}`);
}

window.onload = updateCourseList;

export default class ErrorManager {
    static showProjectDataError() {
        alert("Project data error");
    }

    static catchError(error) {
        console.error(error);
    }
}
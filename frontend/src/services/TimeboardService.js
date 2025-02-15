import HttpService from "./HttpService";
import {
  SERVER_BASE_URL,
  DURATIONS_LASTWEEK_URL,
  DURATIONS_TOTAL_URL,
  PERSONAL_DURATIONS_URL,
  PERSONAL_INTERVALS_URL,
} from "../shared/serverUrls.js";

export default class TimeboardService {
  // TODO: move this to somewhere robust
  static frontEndURL() {
    return "http://localhost:3000/";
  }

  // Get logged minutes of all users of last week
  static getMinutesLastWeek() {
    return new Promise((resolve, reject) => {
      HttpService.get(
        SERVER_BASE_URL + DURATIONS_LASTWEEK_URL,
        (data) => {
          resolve(JSON.parse(data));
        },
        (errorMsg) => {
          reject(errorMsg);
        }
      );
    });
  }

  // Get logged minutes of all users of all time
  static getMinutesWholeTime() {
    return new Promise((resolve, reject) => {
      HttpService.get(
        SERVER_BASE_URL + DURATIONS_TOTAL_URL,
        (data) => {
          resolve(JSON.parse(data));
        },
        (errorMsg) => {
          reject(errorMsg);
        }
      );
    });
  }

  // Get logged intervals of current user of all time, data from server contains pairs of date and integer, date could
  // be transfered only as string and must be converted to type `Date'.
  static getPersonalIntervals() {
    return new Promise((resolve, reject) => {
      HttpService.get(
        SERVER_BASE_URL + PERSONAL_INTERVALS_URL,
        (data) => {
          resolve(JSON.parse(data));
        },
        (errorMsg) => {
          reject(errorMsg);
        }
      );
    });
  }

  // Get logged durations of current user of all time, data from server contains pairs of date and integer, date could
  // be transfered only as string and must be converted to type `Date'.
  static getPersonalDurations() {
    return new Promise((resolve, reject) => {
      HttpService.get(
        SERVER_BASE_URL + PERSONAL_DURATIONS_URL,
        (data) => {
          resolve(JSON.parse(data));
        },
        (errorMsg) => {
          reject(errorMsg);
        }
      );
    });
  }
}

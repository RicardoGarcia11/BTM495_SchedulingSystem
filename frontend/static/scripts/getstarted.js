import React from "react";
import { PropertyDefault } from "./PropertyDefault";
import { SchedulingApp } from "./SchedulingApp";
import "./style.css";

export const GetStartedPage = () => {
  return (
    <div className="get-started-page">
      <div className="div">
        <p className="p">Book, Track, and Organize your tasks easily</p>

        <div className="text-wrapper-2">Manage Your Schedule Efficiently</div>

        <SchedulingApp
          className="scheduling-app-banner"
          divClassName="scheduling-app-instance"
        />
        <PropertyDefault className="button-transition" text="Get Started" />
        <PropertyDefault className="property-1-default" text="Login" />
      </div>
    </div>
  );
};


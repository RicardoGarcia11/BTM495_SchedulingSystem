import React from "react";
import { PropertyDefault } from "./PropertyDefault";
import "./style.css";

export const SignUpPage = () => {
  return (
    <div className="sign-up-page">
      <div className="div">
        <div className="text-wrapper">Full Name</div>

        <div className="login-2">Email</div>

        <div className="login-3">Create New Password</div>

        <div className="login-4">Confirm Password</div>

        <div className="rectangle" />

        <div className="rectangle-2" />

        <div className="rectangle-3" />

        <div className="rectangle-4" />

        <div className="login-5">SIGN UP</div>

        <PropertyDefault
          className="button-transition"
          loginClassName="property-1-default"
          text="Create Account"
        />
      </div>
    </div>
  );
};

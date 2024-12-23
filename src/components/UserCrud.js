import React, { useState } from "react";
import axios from "axios";
import "./UserCrudStyle.css";
import bcrypt from "bcryptjs";

const apiBaseUrl = "https://yonst2cr18.execute-api.us-east-2.amazonaws.com/Test1/users";


const InputField = ({ label, name, type = "text", value, onChange, error, required = false }) => (
  <div style={{ marginBottom: "10px" }}>
    <label>
      {label} {required && <span style={{ color: "red" }}>*</span>}
    </label>
    <input
      type={type}
      name={name}
      value={value}
      onChange={onChange}
      style={{ display: "block", width: "100%" }}
    />
    {error && <span style={{ color: "red", fontSize: "12px" }}>{error}</span>}
  </div>
);

function UserCrud() {
  
  const [forms, setForms] = useState({
    create: { email: "", first_name: "", last_name: "", password_hash: "" },
    fetch: { email: "" },
    update: { email: "", first_name: "", last_name: "" },
    delete: { email: "" },
  });

  
  const [errors, setErrors] = useState({
    create: {},
    fetch: {},
    update: {},
    delete: {},
  });

  const [responseMessage, setResponseMessage] = useState("");
  const [userData, setUserData] = useState(null);

  
  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const validateForm = (formName) => {
    const formErrors = {};
    const form = forms[formName];

    
    Object.entries(form).forEach(([key, value]) => {
      if (!value) formErrors[key] = `${key.replace("_", " ")} is required.`;
      if (key === "email" && value && !validateEmail(value)) {
        formErrors.email = "Invalid email format.";
      }
    });

    setErrors((prevErrors) => ({ ...prevErrors, [formName]: formErrors }));
    return Object.keys(formErrors).length === 0; // Return true if no errors
  };

  const handleInputChange = (e, formName) => {
    const { name, value } = e.target;
    setForms((prevForms) => ({
      ...prevForms,
      [formName]: { ...prevForms[formName], [name]: value },
    }));
  };

  
  const createUser = async () => {
    if (!validateForm("create")) return;

    try {
      const hashedPassword = await bcrypt.hash(forms.create.password_hash, 10);
      const payload = { ...forms.create, password_hash: hashedPassword };
      await axios.post(apiBaseUrl, payload);
      alert("User created successfully.");
      setForms((prevForms) => ({ ...prevForms, create: { email: "", first_name: "", last_name: "", password_hash: "" } }));
    } catch (error) {
      setResponseMessage(`Error creating user: ${error.message}`);
    }
  };

  const readUser = async () => {
    if (!validateForm("fetch")) return;

    try {
      const response = await axios.get(apiBaseUrl, { params: { email: forms.fetch.email } });
      setUserData(response.data.user);
    } catch (error) {
      if (error.response?.status === 404) {
        alert("User not found.");
        setUserData(null);
      } else {
        setResponseMessage(`Error fetching user: ${error.message}`);
      }
    }
  };

  const updateUser = async () => {
    if (!validateForm("update")) return;

    try {
      const { email, ...rest } = forms.update;
      const response = await axios.put(`${apiBaseUrl}?email=${email}`, rest);
      alert(response.data.message || response.data.error);
      setForms((prevForms) => ({ ...prevForms, update: { email: "", first_name: "", last_name: "" } }));
    } catch (error) {
      setResponseMessage(`Error updating user: ${error.message}`);
    }
  };

  const deleteUser = async () => {
    if (!validateForm("delete")) return;

    try {
      const response = await axios.delete(apiBaseUrl, { params: { email: forms.delete.email } });
      alert(response.data.message || response.data.error);
      setForms((prevForms) => ({ ...prevForms, delete: { email: "" } }));
    } catch (error) {
      setResponseMessage(`Error deleting user: ${error.message}`);
    }
  };

  return (
    <div className="user-crud-container">
      <h2>User CRUD Operations</h2>

      
      <div className="form-section">
        <h3>Create User</h3>
        {Object.entries(forms.create).map(([key, value]) => (
          <InputField
            key={key}
            label={key.replace("_", " ").toUpperCase()}
            name={key}
            type={key === "password_hash" ? "password" : "text"}
            value={value}
            onChange={(e) => handleInputChange(e, "create")}
            error={errors.create[key]}
            required
          />
        ))}
        <button onClick={createUser}>Create User</button>
      </div>

      
      <div className="form-section">
        <h3>Read User</h3>
        <InputField
          label="Email"
          name="email"
          value={forms.fetch.email}
          onChange={(e) => handleInputChange(e, "fetch")}
          error={errors.fetch.email}
          required
        />
        <button onClick={readUser}>Fetch User</button>
        {userData && (
          <div>
            <h3>User Information</h3>
            <p>Email: {userData.email}</p>
            <p>First Name: {userData.first_name}</p>
            <p>Last Name: {userData.last_name}</p>
          </div>
        )}
      </div>

     
      <div className="form-section">
        <h3>Update User</h3>
        {Object.entries(forms.update).map(([key, value]) => (
          <InputField
            key={key}
            label={key.replace("_", " ").toUpperCase()}
            name={key}
            value={value}
            onChange={(e) => handleInputChange(e, "update")}
            error={errors.update[key]}
            required
          />
        ))}
        <button onClick={updateUser}>Update User</button>
      </div>

      
      <div className="form-section">
        <h3>Delete User</h3>
        <InputField
          label="Email"
          name="email"
          value={forms.delete.email}
          onChange={(e) => handleInputChange(e, "delete")}
          error={errors.delete.email}
          required
        />
        <button onClick={deleteUser}>Delete User</button>
      </div>

      {responseMessage && <div className="response-message">{responseMessage}</div>}
    </div>
  );
}

export default UserCrud;
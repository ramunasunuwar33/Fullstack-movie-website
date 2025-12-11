import React, { useState, useEffect } from "react";
import styles from "../assets/css/user_profile.module.css";
import { useAuth } from "../context/useAuth";
import Navbar from "../components/navbar";
import {get_user_profile} from "../api/endpoints";
import { useNavigate } from "react-router-dom";
import { FaEdit } from "react-icons/fa";


const Profile = () => {

  
  const {user , logoutUser}= useAuth();
  const [userprofile, setUserProfile] = useState([]);
  const navigate = useNavigate();

  const fetchUserProfile = async()=>{
    const response = await get_user_profile();
    setUserProfile(response);
  }

  useEffect(() => {
    fetchUserProfile();
    }, []);

  const handleLogout = async () => {
    await logoutUser();
    navigate("/login");
  };

  return (
    <div className={styles.profileContainer}>
        <Navbar/>
      <div className={styles.profileCard}>
        {/* Profile Image */}
        <img src={userprofile.image} alt="Profile" className={styles.profileImage} />
        
        {/* User Info */}
        <h2>{user.first_name}</h2>
        <p>{user.email}</p>

        {/* Action Buttons */}
        <div className={styles.actions}>
          <button className={styles.cancelBtn} onClick={handleLogout}>Logout</button>
          <a className={styles.edit_btn} href="/edit_profile"><FaEdit/><p>Edit</p></a>
          </div>
        </div>
      </div>
  );
};

export default Profile;

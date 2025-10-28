import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

function Register() {
  const [formData, setFormData] = useState({username: '', email: '', password: '', confirmPassword: '', full_name: '', role: 'student'});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { register } = useAuth();

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (formData.password !== formData.confirmPassword) {
      setError('Mật khẩu xác nhận không khớp');
      return;
    }
    setLoading(true);
    try {
      const { confirmPassword, ...userData } = formData;
      const response = await register(userData);
      navigate(response.user.role === 'teacher' ? '/teacher' : '/chat');
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng ký thất bại');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="auth-header">
          <h1>🎓 Chatbot Tâm Lý</h1>
          <p>Hỗ trợ tâm lý học sinh</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Đăng Ký</h2>
          {error && <div className="error-message">{error}</div>}
          <div className="form-group">
            <label>Họ và tên</label>
            <input type="text" name="full_name" value={formData.full_name} onChange={handleChange} placeholder="Nhập họ và tên" required />
          </div>
          <div className="form-group">
            <label>Tên đăng nhập</label>
            <input type="text" name="username" value={formData.username} onChange={handleChange} placeholder="Nhập tên đăng nhập" required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" name="email" value={formData.email} onChange={handleChange} placeholder="Nhập email" required />
          </div>
          <div className="form-group">
            <label>Vai trò</label>
            <select name="role" value={formData.role} onChange={handleChange}>
              <option value="student">Học sinh</option>
              <option value="teacher">Giáo viên</option>
            </select>
          </div>
          <div className="form-group">
            <label>Mật khẩu</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} placeholder="Nhập mật khẩu" required />
          </div>
          <div className="form-group">
            <label>Xác nhận mật khẩu</label>
            <input type="password" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} placeholder="Nhập lại mật khẩu" required />
          </div>
          <button type="submit" disabled={loading} className="auth-button">
            {loading ? 'Đang đăng ký...' : 'Đăng Ký'}
          </button>
          <p className="auth-link">
            Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Register;

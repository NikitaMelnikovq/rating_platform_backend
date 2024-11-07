// src/components/TeacherDisciplineCreateMain.jsx

import React, { useState, useEffect } from 'react';
import '../../styles/TeacherDisciplineCreate/teacherDisciplineCreateMain.css';
import { ChevronLeft, Trash2, ChevronDown } from 'lucide-react';
import axios from 'axios'; // Используем axios напрямую
import { useAuth } from '../../contexts/AuthContext'; // Предполагается, что у вас есть контекст для аутентификации

const TeacherDisciplineCreateMain = () => {
    const [discipline, setDiscipline] = useState('');
    const [isShaking, setIsShaking] = useState(false);
    const [disciplines, setDisciplines] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const { token } = useAuth(); // Получаем токен из контекста аутентификации

    // Конфигурация заголовков для axios
    const axiosInstance = axios.create({
        baseURL: 'http://localhost:8000/', // Замените на ваш базовый URL
        headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    // Функция для получения списка дисциплин
    const fetchDisciplines = async () => {
        try {
            const response = await axiosInstance.get('/api/subjects/');
            setDisciplines(response.data);
        } catch (error) {
            console.error('Ошибка при получении дисциплин:', error);
        }
    };

    useEffect(() => {
        fetchDisciplines();
    }, []);

    // Функция для добавления дисциплины
    const handleAddDiscipline = async () => {
        const trimmedDiscipline = discipline.trim();
        if (trimmedDiscipline && !disciplines.some(d => d.name.toLowerCase() === trimmedDiscipline.toLowerCase())) {
            try {
                const response = await axiosInstance.post('/api/subjects/', { name: trimmedDiscipline });
                setDisciplines([...disciplines, response.data]);
                setDiscipline(''); // Очистить поле ввода
                setIsOpen(false);
            } catch (error) {
                console.error('Ошибка при добавлении дисциплины:', error);
            }
        }
    };

    // Функция для удаления дисциплины
    const handleDelete = async (id) => {
        setIsShaking(true);
        try {
            await axiosInstance.delete(`/api/subjects/${id}/`);
            setDisciplines(disciplines.filter(d => d.id !== id));
        } catch (error) {
            console.error('Ошибка при удалении дисциплины:', error);
        } finally {
            setTimeout(() => setIsShaking(false), 820);
        }
    };

    // Обработчик выбора дисциплины из списка
    const handleSelectOption = (option) => {
        setDiscipline(option.name);
        setIsOpen(false);
    };

    // Обработчик изменения ввода
    const handleInputChange = (e) => {
        setDiscipline(e.target.value);
    };

    return (
        <main className="teacher-discipline-create__main">
            <div className="teacher-discipline-create__main-container">
                <button className="teacher-discipline-create__back-btn">
                    <ChevronLeft size={24} />
                </button>
                <div className="teacher-discipline-create__content">
                    <div className="teacher-discipline-create__input-group">
                        <label htmlFor="discipline" className="teacher-discipline-create__label">Дисциплина</label>
                        <div className="teacher-discipline-create__custom-select">
                            <input
                                type="text"
                                id="discipline"
                                className="teacher-discipline-create__input"
                                value={discipline}
                                onChange={handleInputChange}
                                onFocus={() => setIsOpen(true)}
                                placeholder="Выберите или введите дисциплину"
                            />
                            <button
                                type="button"
                                className="teacher-discipline-create__dropdown-toggle"
                                onClick={() => setIsOpen(!isOpen)}
                            >
                                <ChevronDown size={20} />
                            </button>
                            {isOpen && (
                                <ul className="teacher-discipline-create__options">
                                    {disciplines.map((option) => (
                                        <li
                                            key={option.id}
                                            onClick={() => handleSelectOption(option)}
                                            className="teacher-discipline-create__option"
                                        >
                                            {option.name}
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>
                    <div className="teacher-discipline-create__actions">
                        <button className="teacher-discipline-create__apply-btn" onClick={handleAddDiscipline}>
                            Применить
                        </button>
                        <button
                            className={`teacher-discipline-create__delete-btn ${isShaking ? 'shake' : ''}`}
                            onClick={() => {
                                if (discipline) {
                                    const selectedDiscipline = disciplines.find(d => d.name === discipline);
                                    if (selectedDiscipline) {
                                        handleDelete(selectedDiscipline.id);
                                    }
                                }
                            }}
                            disabled={!discipline}
                        >
                            <Trash2 size={24} />
                        </button>
                    </div>
                </div>
            </div>
        </main>
    );
};

export default TeacherDisciplineCreateMain;

import { useTheme } from "../../contexts/ThemeContext";
import { useSettings } from "../context/SettingsContext";

export default function useThemeSettings() {
  const { theme, toggleTheme, isDark } = useTheme();
  const { dispatch } = useSettings();
  
  const changeTheme = (value) => {
    // Map the value to the existing theme system
    if (value === 'dark' && theme === 'light') {
      toggleTheme();
    } else if (value === 'light' && theme === 'dark') {
      toggleTheme();
    }
    dispatch({ type: "SET_THEME", payload: value });
  };
  
  return { theme, changeTheme };
}

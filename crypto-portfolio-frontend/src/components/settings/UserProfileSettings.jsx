import useUserSettings from "./hooks/useUserSettings";
import useFileUpload   from "./hooks/useFileUpload";
import { useSettingsValidation } from "./hooks/useSettingsValidation";

export default function UserProfileSettings() {
  const { user, updateUser } = useUserSettings();
  const { file, preview, onSelect } = useFileUpload();
  const { validateEmail, validatePhone } = useSettingsValidation();

  const save = (e) => {
    e.preventDefault();
    if (!validateEmail(user.email) || !validatePhone(user.phone)) return alert("Invalid details");
    updateUser({ avatar: preview || user.avatar });
    alert("Profile updated!");
  };

  return (
    <section>
      <h2 className="text-xl font-semibold mb-4">Profile</h2>
      <form onSubmit={save} className="space-y-4">
        <div className="flex items-center gap-4">
          <label className="relative cursor-pointer">
            <img
              src={preview || user.avatar || `https://api.dicebear.com/6.x/initials/svg?seed=${user.name}`}
              alt="avatar"
              className="w-20 h-20 rounded-full object-cover"
            />
            <input type="file" accept="image/*" onChange={onSelect} className="absolute inset-0 opacity-0" />
          </label>
          <div className="flex-1 space-y-2">
            <input
              type="text"
              value={user.name}
              onChange={(e) => updateUser({ name: e.target.value })}
              placeholder="Full Name"
              className="input w-full"
            />
            <input
              type="email"
              value={user.email}
              onChange={(e) => updateUser({ email: e.target.value })}
              placeholder="Email"
              className="input w-full"
            />
            <input
              type="tel"
              value={user.phone}
              onChange={(e) => updateUser({ phone: e.target.value })}
              placeholder="Phone"
              className="input w-full"
            />
          </div>
        </div>
        <button className="btn-primary">Save Profile</button>
      </form>
    </section>
  );
}

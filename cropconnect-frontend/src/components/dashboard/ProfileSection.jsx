import { toast } from "sonner";
import { INDIA_STATES, getDistrictOptions, getPlaceOptions } from "../../lib/indiaLocations";

const profileSelectClass = "min-w-[190px] max-w-[260px] rounded border border-gray-300 px-3 py-1 text-right";

export default function ProfileSection({ ctx }) {
  const {
    EMPTY_DISPLAY,
    colors,
    cropZones,
    displayValue,
    editData,
    isEditingProfile,
    isPresent,
    saveUserToMysql,
    setEditData,
    setIsEditingProfile,
    setUserData,
    userData,
  } = ctx;

  const editLocationType = (editData.locationType || userData.locationType || "city") === "village" ? "village" : "city";
  const editState = editData.state || userData.state || "";
  const editDistrict = editData.district || userData.district || "";
  const profileDistrictOptions = getDistrictOptions(editState);
  const profilePlaceOptions = getPlaceOptions(editState, editDistrict);
  const handleProfileFieldChange = (key, value) => {
    setEditData((prev) => {
      const next = { ...prev, [key]: value };
      if (key === "state") {
        next.district = "";
        next.city = "";
        next.village = "";
      }
      if (key === "district" || key === "locationType") {
        next.city = "";
        next.village = "";
      }
      return next;
    });
  };

  const handleEditProfile = async () => {
    if (isEditingProfile) {
      const updatedUser = { ...userData, ...editData };
      const location = updatedUser.locationType === "village"
        ? updatedUser.village || updatedUser.city || ""
        : updatedUser.city || updatedUser.village || "";

      setUserData(updatedUser);

      try {
        const mysqlUser = await saveUserToMysql({
          name: updatedUser.name,
          phone: updatedUser.phone,
          state: updatedUser.state,
          district: updatedUser.district || "",
          location,
          location_type: updatedUser.locationType || "city",
          city: updatedUser.city || "",
          village: updatedUser.village || "",
          land_size: updatedUser.landSize ? Number(updatedUser.landSize) : null,
          sensors: updatedUser.sensors || "0",
          pumps: updatedUser.pumps || "0",
        });
        const mergedUser = mysqlUser ? { ...updatedUser, ...mysqlUser } : updatedUser;
        setUserData(mergedUser);
        toast.success("Profile updated in MySQL!");
      } catch (error) {
        toast.error(error.message || "Profile saved locally, but MySQL update failed");
      }
    } else {
      setEditData(userData);
    }
    setIsEditingProfile(!isEditingProfile);
  };

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl border shadow-sm" style={{ background: colors.cream, borderColor: colors.creamDark }}>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-full flex items-center justify-center text-2xl font-bold" style={{ background: colors.greenDark, color: "white" }}>
              <span data-no-translate="true">{userData.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)}</span>
            </div>
            <div>
              <h3 data-no-translate="true" className="text-xl font-semibold" style={{ color: colors.textDark }}>{userData.name}</h3>
              <p data-no-translate="true" className="text-sm" style={{ color: colors.textMid }}>{userData.email}</p>
            </div>
          </div>
          <button
            onClick={handleEditProfile}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isEditingProfile
                ? "bg-green-600 text-white"
                : "bg-gray-100 hover:bg-gray-200"
            }`}
            style={{ color: isEditingProfile ? "white" : colors.textDark }}
          >
            {isEditingProfile ? "Save" : "Edit Profile"}
          </button>
        </div>

        <div className="space-y-4">
          {[
            { label: "Full Name", key: "name", type: "text" },
            { label: "Email", key: "email", type: "email" },
            { label: "State", key: "state", type: "state" },
            { label: "Location Type", key: "locationType", type: "locationType" },
            { label: "District", key: "district", type: "district" },
            { label: editLocationType === "city" ? "City" : "Village", key: editLocationType === "city" ? "city" : "village", type: "place" },
            { label: "Land Size (acres)", key: "landSize", type: "text" },
            { label: "Crop Type", key: "cropType", type: "text" },
            { label: "Farming Type", key: "farmingType", type: "text" },
            { label: "Zone A (Crops)", key: "zoneA", type: "text" },
            { label: "Zone B (Crops)", key: "zoneB", type: "text" },
            { label: "Zone C (Crops)", key: "zoneC", type: "text" },
          ].map((field) => (
            <div key={field.key} className="flex justify-between items-center py-3 border-b" style={{ borderColor: colors.creamDark }}>
              <span className="font-medium" style={{ color: colors.textDark }}>{field.label}</span>
              {isEditingProfile ? (
                field.type === "state" ? (
                  <select
                    value={editData.state || ""}
                    onChange={(event) => handleProfileFieldChange("state", event.target.value)}
                    className={profileSelectClass}
                    style={{ background: colors.cream, color: colors.textDark }}
                  >
                    <option value="">Select state</option>
                    {INDIA_STATES.map((state) => (
                      <option key={state.code} value={state.name}>
                        {state.name}
                      </option>
                    ))}
                  </select>
                ) : field.type === "locationType" ? (
                  <select
                    value={editLocationType}
                    onChange={(event) => handleProfileFieldChange("locationType", event.target.value)}
                    className={profileSelectClass}
                    style={{ background: colors.cream, color: colors.textDark }}
                  >
                    <option value="city">City</option>
                    <option value="village">Village</option>
                  </select>
                ) : field.type === "district" ? (
                  <select
                    value={editData.district || ""}
                    onChange={(event) => handleProfileFieldChange("district", event.target.value)}
                    disabled={!editState}
                    className={`${profileSelectClass} disabled:opacity-50`}
                    style={{ background: colors.cream, color: colors.textDark }}
                  >
                    <option value="">{editState ? "Select district" : "Select state first"}</option>
                    {profileDistrictOptions.map((district) => (
                      <option key={district} value={district}>
                        {district}
                      </option>
                    ))}
                  </select>
                ) : field.type === "place" ? (
                  <select
                    value={editData[field.key] || ""}
                    onChange={(event) => handleProfileFieldChange(field.key, event.target.value)}
                    disabled={!editDistrict}
                    className={`${profileSelectClass} disabled:opacity-50`}
                    style={{ background: colors.cream, color: colors.textDark }}
                  >
                    <option value="">{editDistrict ? `Select ${field.label.toLowerCase()}` : "Select district first"}</option>
                    {profilePlaceOptions.map((place) => (
                      <option key={place} value={place}>
                        {place}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={field.type}
                    value={editData[field.key] || ""}
                    onChange={(e) => setEditData({ ...editData, [field.key]: e.target.value })}
                    className="px-3 py-1 rounded border border-gray-300 text-right"
                    style={{ color: colors.textMid }}
                  />
                )
              ) : (
                <span data-dynamic-value="true" style={{ color: colors.textMid }}>{displayValue(userData[field.key])}</span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="p-5 rounded-xl border shadow-sm" style={{ background: colors.cream, borderColor: colors.creamDark }}>
        <h3 className="font-semibold mb-4" style={{ color: colors.textDark }}>Farm Statistics</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 rounded-lg" style={{ background: colors.cream }}>
            <p className="text-sm" style={{ color: colors.textMid }}>Total Area</p>
            <p className="text-xl font-bold" style={{ color: colors.textDark }}>{displayValue(userData.landSize, " acres")}</p>
          </div>
          <div className="p-4 rounded-lg" style={{ background: colors.cream }}>
            <p className="text-sm" style={{ color: colors.textMid }}>Zones</p>
            <p className="text-xl font-bold" style={{ color: colors.textDark }}>{cropZones.filter((zone) => isPresent(zone.crop)).length || EMPTY_DISPLAY}</p>
          </div>
          <div className="p-4 rounded-lg" style={{ background: colors.cream }}>
            <p className="text-sm" style={{ color: colors.textMid }}>Active Sensors</p>
            <p className="text-xl font-bold" style={{ color: colors.textDark }}>{userData.sensors}</p>
          </div>
          <div className="p-4 rounded-lg" style={{ background: colors.cream }}>
            <p className="text-sm" style={{ color: colors.textMid }}>Irrigation Pumps</p>
            <p className="text-xl font-bold" style={{ color: colors.textDark }}>{userData.pumps}</p>
          </div>
        </div>
      </div>

      <div className="p-5 rounded-xl border shadow-sm" style={{ background: colors.cream, borderColor: colors.creamDark }}>
        <h3 className="font-semibold mb-4" style={{ color: colors.textDark }}>Zone Details</h3>
        <div className="space-y-3">
          {[
            { zone: "Zone A", crops: userData.zoneA, area: "", status: userData.zoneA ? "Active" : "" },
            { zone: "Zone B", crops: userData.zoneB, area: "", status: userData.zoneB ? "Active" : "" },
            { zone: "Zone C", crops: userData.zoneC, area: "", status: userData.zoneC ? "Active" : "" },
          ].map((zone) => (
            <div key={zone.zone} className="flex items-center justify-between p-3 rounded-lg" style={{ background: colors.cream }}>
              <div>
                <p className="font-medium" style={{ color: colors.textDark }}>{zone.zone}</p>
                <p className="text-sm" style={{ color: colors.textMid }}>{zone.crops} - {zone.area}</p>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full ${zone.status === "Active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"}`}>
                {displayValue(zone.status)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

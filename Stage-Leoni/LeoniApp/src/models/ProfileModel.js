class ProfileModel {
  constructor(data = {}) {
    this.userId = data.userId || null;
    this.firstName = data.firstName || '';
    this.lastName = data.lastName || '';
    this.email = data.email || '';
    this.phone = data.phone || '';
    this.address = data.address || '';
    this.department = data.department || '';
    this.position = data.position || '';
    this.createdAt = data.createdAt || new Date();
    this.updatedAt = data.updatedAt || new Date();
  }

  toJSON() {
    return {
      userId: this.userId,
      firstName: this.firstName,
      lastName: this.lastName,
      email: this.email,
      phone: this.phone,
      address: this.address,
      department: this.department,
      position: this.position,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

export default ProfileModel;

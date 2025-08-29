// lib/candidateUtils.ts

export interface BackendCandidate {
  name: string;
  relevant_content: string;
  cv_link: string;
}

export interface FrontendCandidate {
  id: string;
  name: string;
  role: string;
  avatar: string;
  skills: string[];
  location: string;
  experience: string;
  cvUrl: string;
  initials: string;
  gradientFrom: string;
  gradientTo: string;
}

// Extract role from relevant_content (simple heuristic)
const extractRoleFromContent = (content: string): string => {
  const roleKeywords = [
    'developer', 'engineer', 'designer', 'manager', 'analyst', 
    'specialist', 'consultant', 'architect', 'lead', 'senior',
    'junior', 'frontend', 'backend', 'fullstack', 'software'
  ];
  
  const sentences = content.split('.');
  for (const sentence of sentences) {
    for (const keyword of roleKeywords) {
      if (sentence.toLowerCase().includes(keyword)) {
        return sentence.trim();
      }
    }
  }
  
  return "Professional Candidate";
};

// Extract skills from relevant_content
const extractSkillsFromContent = (content: string): string[] => {
  const commonSkills = [
    'react', 'typescript', 'javascript', 'python', 'java', 'node', 
    'aws', 'docker', 'kubernetes', 'sql', 'nosql', 'html', 'css',
    'vue', 'angular', 'django', 'flask', 'fastapi', 'postgresql',
    'mongodb', 'git', 'ci/cd', 'agile', 'scrum', 'rest', 'graphql'
  ];
  
  const foundSkills: string[] = [];
  const contentLower = content.toLowerCase();
  
  commonSkills.forEach(skill => {
    if (contentLower.includes(skill)) {
      foundSkills.push(skill.charAt(0).toUpperCase() + skill.slice(1));
    }
  });
  
  return foundSkills.length > 0 ? foundSkills : ["Skills: See CV"];
};

// Generate gradient colors based on name (deterministic)
const generateGradientFromName = (name: string): { from: string; to: string } => {
  const colors = [
    { from: "#667eea", to: "#764ba2" },
    { from: "#f093fb", to: "#f5576c" },
    { from: "#4facfe", to: "#00f2fe" },
    { from: "#43e97b", to: "#38f9d7" },
    { from: "#fa709a", to: "#fee140" },
    { from: "#30cfd0", to: "#330867" }
  ];
  
  // Simple hash based on name to pick consistent colors
  const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
};

// Transform backend candidate to frontend candidate
export const transformBackendCandidate = (backendCandidate: BackendCandidate): FrontendCandidate => {
  const initials = backendCandidate.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
  
  const gradient = generateGradientFromName(backendCandidate.name);
  
  return {
    id: `${backendCandidate.name.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}`,
    name: backendCandidate.name,
    role: extractRoleFromContent(backendCandidate.relevant_content),
    avatar: "",
    skills: extractSkillsFromContent(backendCandidate.relevant_content),
    location: "Location: See CV", // Backend doesn't provide location
    experience: "Experience: See CV", // Backend doesn't provide experience
    cvUrl: backendCandidate.cv_link,
    initials,
    gradientFrom: gradient.from,
    gradientTo: gradient.to
  };
};